#! /usr/bin/env python2

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Jonathan Sanchez wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------

import dbus
import time
import sys
import gobject
import dnslib
from dnslib.server import DNSServer, DNSLogger
from dbus.mainloop.glib import DBusGMainLoop

PARENT_DOMAIN = '.subnet.lan'
ZONE_FILE = '/etc/named/avahi-discover'

AVAHI_DBUS_NAME = 'org.freedesktop.Avahi'
AVAHI_DBUS_PATH_SERVER = '/'

AVAHI_DBUS_INTERFACE_SERVER = 'org.freedesktop.Avahi.Server'
AVAHI_DBUS_INTERFACE_SERVICE_TYPE_BROWSER = (
    'org.freedesktop.Avahi.ServiceTypeBrowser')
AVAHI_DBUS_INTERFACE_SERVICE_BROWSER = (
    'org.freedesktop.Avahi.ServiceBrowser')

AVAHI_PROTO_UNSPEC = -1
AVAHI_IF_UNSPEC = -1


class AvahiBrowser:
    service_type_browsers = {}
    service_browsers = {}
    dicovered = {}

    def connect(self):
        self.bus = dbus.SystemBus()
        self.server = dbus.Interface(
            self.bus.get_object(AVAHI_DBUS_NAME, AVAHI_DBUS_PATH_SERVER),
            AVAHI_DBUS_INTERFACE_SERVER
        )

    def new_service(self, interface, protocol, name, stype, domain, flags):
        print(u'service found {} {} {}'.format(
            unicode(domain), unicode(name), unicode(stype)))
        self.server.ResolveService(
            interface,
            protocol,
            name,
            stype,
            domain,
            AVAHI_PROTO_UNSPEC,
            dbus.UInt32(0),
            reply_handler=self.service_resolved,
            error_handler=self.print_error
        )

    def service_resolved(
            self, interface, protocol, name, stype,
            domain, host, aprotocol, address, port, txt, flags):
        self.dicovered[unicode(host)] = unicode(address)
        # self.write_dns()

    def print_error(self, err):
        print(err)

    def browse_domain(self, domain, stype=None):
        interface = AVAHI_IF_UNSPEC
        protocol = AVAHI_PROTO_UNSPEC
        flags = dbus.UInt32(0)

        # Are we already browsing this domain?

        if stype is None:
            if not (interface, protocol, domain) in self.service_type_browsers:
                print("Browsing domain '%s'..." % (domain, ))

                b = dbus.Interface(
                    self.bus.get_object(
                        AVAHI_DBUS_NAME,
                        self.server.ServiceTypeBrowserNew(
                            interface,
                            protocol,
                            domain,
                            flags
                        )
                    ),
                    AVAHI_DBUS_INTERFACE_SERVICE_TYPE_BROWSER
                )
                self.service_type_browsers[(interface, protocol, domain)] = b

                b.connect_to_signal('ItemNew', self.new_service_type)
        else:
            self.new_service_type(interface, protocol, stype, domain, flags)

    def new_service_type(self, interface, protocol, stype, domain, flags):
        # Are we already browsing this domain for this type?
        if not (interface, protocol, stype, domain) in self.service_browsers:

            print("Browsing for services '%s' in '%s'" % (stype, domain))

            b = dbus.Interface(
                self.bus.get_object(
                    AVAHI_DBUS_NAME,
                    self.server.ServiceBrowserNew(
                        interface,
                        protocol,
                        stype,
                        domain,
                        dbus.UInt32(0)
                    )
                ),
                AVAHI_DBUS_INTERFACE_SERVICE_BROWSER
            )
            b.connect_to_signal('ItemNew', self.new_service)

            self.service_browsers[(interface, protocol, stype, domain)] = b

    def print_table(self):
        for domain, address in self.dicovered.items():
            print('| %-40s | %-20s |' % (domain, address))

    def write_dns(self):
        dns = dnslib.DNSRecord()
        for domain, address in self.dicovered.items():
            dns.add_ar(
                dnslib.RR(
                    domain.replace(
                        '.local',
                        PARENT_DOMAIN
                    ),
                    rdata=dnslib.A(address)
                )
            )

        f = open(ZONE_FILE, 'w')
        f.write(str(dns))
        f.close()

    def resolve(self, request, handler):
        print('resolve')
        reply = request.reply()
        # dnslib.RR(
        #     domain.replace(
        #         '.local',
        #         PARENT_DOMAIN
        #     ),
        #     rdata=dnslib.A(address)
        # )
        reply.add_answer(dnslib.RR(
            'hello.subnet.lan',
            rdata=dnslib.A('192.168.0.0')
        ))
        return reply


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    try:
        resolver = AvahiBrowser()

        logger = DNSLogger(prefix=False)
        server = DNSServer(
            resolver,
            port=8053,
            address='0.0.0.0',
            # tcp=True,
            logger=logger)

        resolver.connect()

        # scanner.browse_domain("local", "_ssh._tcp")
        resolver.browse_domain('local')
        server.start_thread()
        # server.start()

    except dbus.DBusException as e:
        print("Failed to connect to Avahi, is it running?: {}".format(e))
        sys.exit(1)

    loop = gobject.MainLoop()

    run_forever = True
    if run_forever:
        loop.run()
    else:
        main_context = loop.get_context()

        changed = True
        while changed:
            while main_context.pending():
                changed = True
                main_context.iteration()

            if not changed:
                break

            changed = False
            time.sleep(1)

        # browser.print_table()
        # browser.print_dns()
