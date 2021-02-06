<h1>This repository contains 0x19. Postmortem, tasks for Holberton School.</h1>

<h2>Google Compute Engine Incident #18057</h2>

<h2>Name: Hector Orozco</h2>
<h2>Date: 2021-01-21</h2>

<h2>Status: Complete. Action items in progress</h2>

<h2>Issue Summary:</h2>
<p>On Thursday, 21 January, 2021, Google Compute Engine instances in all regions
lost external connectivity for a total of 18 minutes,
from 19:09 to 19:27 Pacific Time.</p>

<h2>Impact:</h2>
<p>On Thursday, 21 January, 2021 from 19:09 to 19:27 Pacific Time, inbound
internet traffic to Compute Engine instances was not routed correctly,
resulting in dropped connections and an inability to reconnect.
The loss of inbound traffic caused services depending on this network
path to fail as well, including VPNs and L3 network load balancers.
Additionally, the Cloud VPN offering in the asia-east1 region experienced
the same traffic loss starting at an earlier time of 18:14 Pacific Time
but the same end time of 19:27.
This event did not affect Google App Engine, Google Cloud Storage, and other
Google Cloud Platform products; it also did not affect internal connectivity
between GCE services including VMs, HTTP and HTTPS (L7)
load balancers, and outbound internet traffic.</p>

<h2>Timeline:</h2>
<p>Google uses contiguous groups of internet addresses -- known as IP blocks --
for Google Compute Engine VMs, network load balancers, Cloud VPNs, and other
services which need to communicate with users and systems outside of Google.
These IP blocks are announced to the rest of the internet via
the industry-standard BGP protocol, and it is these announcements which allow
systems outside of Google’s network to ‘find’ GCP services regardless of
which network they are on.</p>

<p>At 14:50 Pacific Time on April 11th, our engineers removed an unused
GCE IP block from our network configuration, and instructed Google’s automated
systems to propagate the new configuration across our network.
By itself, this sort of change was harmless and had been performed
previously without incident</p>

<p>One of our core principles at Google is ‘defense in depth’, and Google’s
networking systems have a number of safeguards to prevent them from
propagating incorrect or invalid configurations in the event of an upstream
failure or bug.
These safeguards include a canary step where the configuration is deployed at
a single site and that site is verified to still be working correctly, and a
progressive rollout which makes changes to only a fraction of sites at
a time, so that a novel failure can be caught at an early stage before it
becomes widespread.</p>
<p>As the rollout progressed, those sites which had been announcing GCE IP
blocks ceased to do so when they received the new configuration.
The fault tolerance built into our network design worked correctly and sent
GCE traffic to the the remaining sites which were still announcing
GCE IP blocks. As more and more sites stopped announcing GCE IP
blocks, our internal monitoring picked up two anomalies: first, the Cloud VPN
in asia-east1 stopped functioning at 18:14 because it was announced from fewer
sites than GCE overall, and second, user latency to GCE was anomalously rising
as more and more users were sent to sites which were not close to them.
Google’s Site Reliability Engineers started investigating the problem when
the first alerts were received, but were still trying to determine the root
cause 53 minutes later when the last site announcing GCE IP blocks received the
configuration at 19:07.</p>

<p>With no sites left announcing GCE IP blocks, inbound traffic from the
internet to GCE dropped quickly, reaching >95% loss by 19:09.
Internal monitors generated dozens of alerts in the seconds after the traffic
loss became visible at 19:08, and the Google engineers who had been
investigating a localized failure of the asia-east1 VPN now knew that they
had a widespread and serious problem. They did precisely what we train
for, and decided to revert the most recent configuration changes made
to the network even before knowing for sure what the problem was.
This was the correct action, and the time from detection to decision to
revert to the end of the outage was thus just 18 minutes.
With the immediate outage over, the team froze all configuration changes
to the network, and worked in shifts overnight to ensure first that the systems
were stable and that there was no remaining customer impact, and then to
determine the root cause of the problem.
By 07:00 on January 21 the team was confident that they had established
the root cause as a software bug in the network configuration
management software.</p>

<h2>Root cause(s):</h2>
<p>With both the incident and the immediate risk now over, the engineering
team’s focus is on prevention and mitigation. There are a number of lessons
to be learned from this event -- for example, that the safeguard of a
progressive rollout can be undone by a system designed to mask partial
failures -- which yield similarly-clear actions which we will take, such as
monitoring directly for a decrease in capacity or redundancy even when the
system is still functioning properly. It is our intent to enumerate all
the lessons we can learn from this event, and then to implement all of the
changes which appear useful. As of the time of this writing in the evening of 21
January, there are already 14 distinct engineering changes planned spanning
prevention, detection and mitigation, and that number will increase as our
engineering teams review the incident with other senior engineers across
Google in the coming week. Concretely, the immediate steps we are taking
include:
Monitoring targeted GCE network paths to detect if they change or
cease to function;
Comparing the IP block announcements before and after a network
configuration change to ensure that they are identical in size and coverage.</p>
