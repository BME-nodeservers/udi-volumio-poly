#!/usr/bin/env python3

# Rewrite the NLS file with all the current sources listed.

import os
import in_place

VERSION_FILE = "profile/version.txt"


# Create a dynamic NLS file with the mapping between application ID and
# application names.

def write_nls(logger, player_list):
    logger.info("Writing profile/nls/en_us.txt")
    if not os.path.exists("profile/nls"):
        try:
            os.makedirs("profile/nls")
        except:
            logger.error('unable to create node NLS directory.')

    try:
        nls = open("profile/nls/en_us.txt", "w")

        # Write out the standard node, command, and status entries

        nls.write("# controller\n")
        nls.write("ND-Volumio-NAME = Volumio\n")
        nls.write("ND-Volumio-ICON = Output\n")
        nls.write("ST-ctl-ST-NAME = NodeServer Online\n")
        nls.write("ST-ctl-GV1-NAME = Selected Source\n")
        nls.write("ST-ctl-GV4-NAME = Shuffle\n")
        nls.write("ST-ctl-GV5-NAME = Repeat\n")
        nls.write("ST-ctl-MODE-NAME = State\n")
        nls.write("ST-ctl-SVOL-NAME = Volume\n")
        nls.write("CMD-ctl-PREV-NAME = Previous\n")
        nls.write("CMD-ctl-NEXT-NAME = Next\n")
        nls.write("CMD-ctl-PLAY-NAME = Play\n")
        nls.write("CMD-ctl-PAUSE-NAME = Pause\n")
        nls.write("CMD-ctl-STOP-NAME = Stop\n")
        nls.write("CMD-ctl-VOLUME-NAME = Volume\n")
        nls.write("CMD-ctl-SHUFFLE-NAME = Shuffle\n")
        nls.write("CMD-ctl-REPEAT-NAME = Repeat\n")
        nls.write("CMD-ctl-SOURCE-NAME = Selected Source\n")
        nls.write("\n")
        nls.write("SWITCH-0 = Off\n")
        nls.write("SWITCH-1 = On\n")
        nls.write("\n")
        nls.write("MODE-0 = Stopped\n")
        nls.write("MODE-1 = Paused\n")
        nls.write("MODE-2 = Playing\n")
        nls.write("\n")

        """
        player_list = { playername: { "node_id": id, "sources": None}, playername1 : {}}
        """
        for rk in player_list:
            node_id = player_list[rk]['node_id']
            nls.write("ND-" + node_id + "-NAME = " + rk + "\n")
            nls.write("ND-" + node_id + "-ICON = Output\n")
            nls.write("\n")
            for src in player_list[rk]['sources']:
                logger.debug(player_list[rk]['sources'][src])
                (name, cnt) = player_list[rk]['sources'][src]
                nls.write("%s-%d = %s\n" %(node_id, cnt, name))
            nls.write("\n")

        nls.close()
    except:
        logger.error('Failed to write node NLS file.')
        nls.close()


NODEDEF_TMPL = "  <nodeDef id=\"%s\" nodeType=\"139\" nls=\"%s\">\n"
STATUS_TMPL = "      <st id=\"%s\" editor=\"_25_0_R_0_%d_N_%s\" />\n"
LAUNCH_TMPL = "          <p id=\"\" editor=\"_25_0_R_0_%d_N_%s\" init=\"%s\" />\n"
def write_nodedef(logger, player_list):
    logger.info("Writing profile/nodedef/nodedefs.xml")
    nodedef = open("profile/nodedef/nodedefs.xml", "w")

    # First, write the controller node definition
    nodedef.write("<nodeDefs>\n")
    nodedef.write(NODEDEF_TMPL % ('Volumio', 'ctl'))
    nodedef.write("    <sts>\n")
    nodedef.write("      <st id=\"ST\" editor=\"bool\" />\n")
    nodedef.write("    </sts>\n")
    nodedef.write("    <cmds>\n")
    nodedef.write("      <sends />\n")
    nodedef.write("      <accepts>\n")
    nodedef.write("        <cmd id=\"DISCOVER\" />\n")
    nodedef.write("      </accepts>\n")
    nodedef.write("    </cmds>\n")
    nodedef.write("  </nodeDef>\n\n")

    # Loop through and write the node defs for each device
    for rk in player_list:
        logger.debug(player_list)
        src_cnt = len(player_list[rk]['sources'])
        node_id = player_list[rk]['node_id']

        nodedef.write(NODEDEF_TMPL % (node_id, 'ctl'))
        nodedef.write("    <sts>\n")
        nodedef.write("      <st id=\"GV1\" editor=\"_25_0_R_0_%d_N_%s\" />\n" % (src_cnt, node_id))
        nodedef.write("      <st id=\"GV4\" editor=\"SWITCH\" />\n")
        nodedef.write("      <st id=\"GV5\" editor=\"SWITCH\" />\n")
        nodedef.write("      <st id=\"MODE\" editor=\"MODE\" />\n")
        nodedef.write("      <st id=\"SVOL\" editor=\"VOLUME\" />\n")
        nodedef.write("    </sts>\n")
        nodedef.write("    <cmds>\n")
        nodedef.write("      <sends />\n")
        nodedef.write("      <accepts>\n")
        nodedef.write("        <cmd id=\"SOURCE\">\n")
        nodedef.write(LAUNCH_TMPL % (src_cnt, node_id, 'GV1'))
        nodedef.write("        </cmd>\n")
        nodedef.write("        <cmd id=\"VOLUME\">\n")
        nodedef.write('           <p id="" editor="VOLUME" init="SVOL"/>\n')
        nodedef.write("        </cmd>\n")
        nodedef.write("        <cmd id=\"PLAY\" />\n")
        nodedef.write("        <cmd id=\"PAUSE\" />\n")
        nodedef.write("        <cmd id=\"STOP\" />\n")
        nodedef.write("        <cmd id=\"PREV\" />\n")
        nodedef.write("        <cmd id=\"NEXT\" />\n")
        nodedef.write("        <cmd id=\"SHUFFLE\">\n")
        nodedef.write('           <p id="" editor="SWITCH" init="GV4"/>\n')
        nodedef.write("        </cmd>\n")
        nodedef.write("        <cmd id=\"REPEAT\">\n")
        nodedef.write('           <p id="" editor="SWITCH" init="GV5"/>\n')
        nodedef.write("        </cmd>\n")
        nodedef.write("      </accepts>\n")
        nodedef.write("    </cmds>\n")
        nodedef.write("  </nodeDef>\n\n")

    nodedef.write("</nodeDefs>\n")

    nodedef.close()

