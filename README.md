# coffeebot
Responsible for watching the office's coffee maker and sending notifications to a Slack channel.

## Known Issues
1. When brewing 2 pots simultaneously, the power can fluctuate more than the threshold of 10 Watts as the power stabilizes. As the pots get done, the bot can interpret this first as 1 fresh pot done and then as 2 old pots being heated. See log file.
2. Heating 1 old pot from off starts power at ~120 Watts which is interpreted as 2 old pots. Power consumption will then slowly lower down to ~65 Watts.
3. Measuring 0.0 and then 0.12 triggers update
## Backlog
- Implement statistics
- Implement reasonable logging
- Alter Slack channel name to show status