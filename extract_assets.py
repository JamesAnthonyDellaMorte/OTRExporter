#!/usr/bin/env python3

import os, sys, shutil
import shutil
from rom_info import Z64Rom
import rom_chooser
import struct
import subprocess
import argparse

def get_default_asset_tool_executable():
    return "x64\\Release\\ZAPD.exe" if sys.platform == "win32" else "../ZAPDTR/ZAPD.out"

def BuildOTR(xmlRoot, xmlVersion, rom, isMM, asset_tool_exe=None, genHeaders=None, customAssetsPath=None, customOtrFile=None, portVer=None):
    if not asset_tool_exe:
        asset_tool_exe = get_default_asset_tool_executable()
    xmlPath = os.path.join(xmlRoot, xmlVersion)
    exec_cmd = [asset_tool_exe, "ed", "-i", xmlPath, "-b", rom, "-fl", "assets/extractor/filelists",
                "-o", "placeholder", "-osf", "placeholder", "-rconf"]
    configFileStr = "assets/extractor/Config_" + xmlVersion + ".xml"
    exec_cmd.extend([configFileStr])

    otrFileName = "oot.o2r"
    if isMM:
        otrFileName = "mm.o2r"


    # generate headers, but not otrs by excluding the otr exporter
    if genHeaders:
        exec_cmd.extend(["-gsf", "1"])
    else:
        # generate otrs, but not headers
        exec_cmd.extend(["-gsf", "0", "-se", "OTR", "--customAssetsPath", customAssetsPath,
                    "--customOtrFile", customOtrFile, "--otrfile", otrFileName])

    if portVer:
        exec_cmd.extend(["--portVer", portVer])

    print(exec_cmd)
    print(os.getcwd())
    exitValue = subprocess.call(exec_cmd)
    if exitValue != 0:
        print("\n")
        print("Error when building the OTR file...", file=os.sys.stderr)
        print("Aborting...", file=os.sys.stderr)
        print("\n")

def BuildCustomOtr(asset_tool_exe=None, assets_path=None, otrfile=None, portVer=None):
    if not asset_tool_exe:
        asset_tool_exe = get_default_asset_tool_executable()

    if not assets_path or not otrfile:
        print("\n")
        print("Assets path or otrfile name not provided. Exiting...", file=os.sys.stderr)
        print("\n")
        return

    exec_cmd = [asset_tool_exe, "botr", "-se", "OTR", "--norom", "--customAssetsPath", assets_path, "--customOtrFile", otrfile]

    if portVer:
        exec_cmd.extend(["--portVer", portVer])

    print(exec_cmd)
    exitValue = subprocess.call(exec_cmd)
    if exitValue != 0:
        print("\n")
        print("Error when building custom otr file...", file=os.sys.stderr)
        print("Aborting...", file=os.sys.stderr)
        print("\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-z", "--asset-tool", "--zapd", help="Path to the asset tool executable", dest="asset_tool_exe", type=str)
    parser.add_argument("rom", help="Path to the rom", type=str, nargs="?")
    parser.add_argument("--non-interactive", help="Runs the script non-interactively for use in build scripts.", dest="non_interactive", action="store_true")
    parser.add_argument("-v", "--verbose", help="Display rom's header checksums and their corresponding xml folder", dest="verbose", action="store_true")
    parser.add_argument("--gen-headers", help="Generate source headers to be checked in", dest="gen_headers", action="store_true")
    parser.add_argument("--norom", help="Generate only custom otr to be bundled to the game", dest="norom", action="store_true")
    parser.add_argument("--xml-root", help="Root path for the rom xmls", dest="xml_root", type=str)
    parser.add_argument("--custom-assets-path", help="Path to custom assets for the custom otr file", dest="custom_assets_path", type=str)
    parser.add_argument("--custom-otr-file", help="Name for custom otr file", dest="custom_otr_file", type=str)
    parser.add_argument("--port-ver", help="Store the port version in the otr", dest="port_ver", type=str)

    args = parser.parse_args()

    if args.norom:
        BuildCustomOtr(args.asset_tool_exe, args.custom_assets_path, args.custom_otr_file, portVer=args.port_ver)
        return

    roms = [ Z64Rom(args.rom) ] if args.rom else rom_chooser.chooseROM(args.verbose, args.non_interactive)
    for rom in roms:
        BuildOTR(args.xml_root, rom.version.xml_ver, rom.file_path, rom.version.is_mm, asset_tool_exe=args.asset_tool_exe, genHeaders=args.gen_headers,
                 customAssetsPath=args.custom_assets_path, customOtrFile=args.custom_otr_file, portVer=args.port_ver)

if __name__ == "__main__":
    main()
