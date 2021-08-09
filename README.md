
# Volumio Node Server (c) 2021 Robert Paauwe

This is a node server to interface a [Volumio](http://www.volumio.org) Music player with
[Universal Devices ISY994] (https://www.universal-devices.com/residential/ISY) series of
controllers. It is written to run under the
[Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/) with
Polyglot V3 running on a [Polisy](https://www.universal-devices.com/product/polisy/)

Volumio is music server software designed to run on lightweight hardware like a Raspberry Pi.
It can play music from multiple sources including a local hard drive, a NAS, music servers,
Internet radio stations, Pandora, Spotify, etc.

This node server allows an ISY to have basic control over the music player. It queries the
Volumio device for the configured sources so that the ISY can choose which source to play.
Play, Pause, Next, Previous playback controls are supported. The ability to adjust the volume
level, turn repeat and shuffle on/off is also available.


## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please.
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web to a free slot.
4. From the Dashboard, select the Volumio node server and go to the configuration tab.
5. Configure the IP address of the Volumio player(s).

### Node Settings
The settings for this node are:

#### Short Poll
   * Not used
#### Long Poll
   * Not used

#### Volumio name / IP Address
   * The list of Volumio devices and their IP addresses.


## Requirements

1. Polyglot V3.
2. ISY firmware 5.3.x or later
3. One or more Volumio music players

# Release Notes

- 2.0.2 08/09/2021
   - Fix source list (remove extra entry)
   - Improve configuration help
- 2.0.1 08/08/2021
   - Removed controller node, it's not used for anything
- 2.0.0 03/12/2021
   - Ported to PG3
   - Added support for multiple Volumio players
- 1.0.0 02/15/2021
   - Initial version published to github
