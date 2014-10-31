#! /usr/bin/env python2

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# Jonathan Sanchez wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------

import avahi
import dbus
import time
import sys
import gobject
import dnslib
from dbus.mainloop.glib import DBusGMainLoop

PARENT_DOMAIN = '.subzone.lan'
ZONE_FILE = '/etc/named/avahi-discover'


class AvahiBrowser:
    service_type_browsers = {}
    service_browsers = {}
    dicovered = {}

    def connect(self):
        self.bus = dbus.SystemBus()
        self.server = dbus.Interface(
            self.bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
            avahi.DBUS_INTERFACE_SERVER
        )

    def new_service(self, interface, protocol, name, stype, domain, flags):
        print(str(domain), str(name), str(stype))
        self.server.ResolveService(
            interface,
            protocol,
            name,
            stype,
            domain,
            avahi.PROTO_UNSPEC,
            dbus.UInt32(0),
            reply_handler=self.service_resolved,
            error_handler=self.print_error
        )

    def service_resolved(
            self, interface, protocol, name, stype,
            domain, host, aprotocol, address, port, txt, flags):
        self.dicovered[str(host)] = str(address)
        self.write_dns()

    def print_error(self, err):
        print(err)

    def browse_domain(self, domain, stype=None):
        interface = avahi.IF_UNSPEC
        protocol = avahi.PROTO_UNSPEC
        flags = dbus.UInt32(0)

        # Are we already browsing this domain?

        if stype is None:
            if not (interface, protocol, domain) in self.service_type_browsers:
                print("Browsing domain '%s'..." % (domain, ))

                b = dbus.Interface(
                    self.bus.get_object(
                        avahi.DBUS_NAME,
                        self.server.ServiceTypeBrowserNew(
                            interface,
                            protocol,
                            domain,
                            flags
                        )
                    ),
                    avahi.DBUS_INTERFACE_SERVICE_TYPE_BROWSER
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
                    avahi.DBUS_NAME,
                    self.server.ServiceBrowserNew(
                        interface,
                        protocol,
                        stype,
                        domain,
                        dbus.UInt32(0)
                    )
                ),
                avahi.DBUS_INTERFACE_SERVICE_BROWSER
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

        print("-" * 20)
        print(dns)
        f = open(ZONE_FILE, 'w')
        f.write(str(dns))
        f.close()


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    try:
        browser = AvahiBrowser()
        browser.connect()

        # scanner.browse_domain("local", "_ssh._tcp")
        browser.browse_domain("local")

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