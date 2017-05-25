

#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo_config import cfg
from oslo_log import log as logging
import socket
from tacker._i18n import _LW
from tacker.common import log
from tacker.vm.monitor_drivers import abstract_driver


LOG = logging.getLogger(__name__)
OPTS = [
    cfg.StrOpt('count', default='1', help=_('number of ICMP packets to send')),
    cfg.StrOpt('timeout', default='1',
               help=_('number of seconds to wait for a response')),
    cfg.StrOpt('sockmode', default='1',
               help=_('socket mode of TCP, UDP(TCP:1, UDP:0)')),
    cfg.StrOpt('scanports', default='80', help=_('number of Target port'))
]
cfg.CONF.register_opts(OPTS, 'monitor_port')


class VNFMonitorPort(abstract_driver.VNFMonitorAbstractDriver):
    def get_type(self):
        return 'port'

    def get_name(self):
        return 'port'

    def get_description(self):
        return 'Tacker VNFMonitor Port Driver'

    def monitor_url(self, plugin, context, device):
        LOG.debug(_('monitor_url %s'), device)
        return device.get('monitor_url', '')

    def portscans(self, count=5, timeout=1, sockmode=1,
                  scanports=80, **kwargs):
        """Checks whether an Target port is reachable by porting.

        :param scanport: target port check
        :param sockmodemode: check socket mode(TCP or UDP)
        :return: bool - True or string 'failure' depending on portability.
        """

        try:
            if sockmode:
                connskt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            else:
                connskt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            connskt.settimeout(timeout)
            # Make a Socket Connection
            result = connskt.connect_ex((kwargs['mgmt_ip'], scanports))
            if result == 0:
                LOG.debug(_("Open ip address: %(ip)s, port: %(ports)s") %
                          {'ip': kwargs['mgmt_ip'], 'ports': scanports})
            else:
                LOG.debug(_("Close ip address: %(ip)s, port: %(ports)s") %
                          {'ip': kwargs['mgmt_ip'], 'ports': scanports})
                connskt.close()
                return 'failure'
            connskt.close()
            # Close the connection
            return True
        except RuntimeError:
            LOG.warning(_LW("Cannot scan port ip address: %(mgmt_ip)s,"
                            " port: %(scanports)d\n"))
            return 'failure'

    @log.log
    def monitor_call(self, device, kwargs):
        if not kwargs['mgmt_ip']:
            return
        return self.portscans(**kwargs)
