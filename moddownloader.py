#!/bin/python3
from urllib import request
from colorama import Fore, Back, Style
import os, argparse, sys, getpass, subprocess, shutil, builtins, pathlib, tarfile

def isDir(path):
	if os.path.isdir(path):
		return path.rstrip('/')
	else:
		raise argparse.ArgumentTypeError(f"{path} is not a valid path")

parser = argparse.ArgumentParser(description='Download mod(s) from Steam Workshop', add_help=False)
parser.add_argument('--username', '-u', required=True, help='Steam username to login with')
parser.add_argument('--app-id', '-a', required=True, help='Application ID for the mod(s)')
parser.add_argument('--batch', '-b', nargs='?', const=True, required=False, default=False, type=bool, help='Download all mods in a single batch (SteamCMD only)')
parser.add_argument('--refresh', '-r', nargs='?', const=True, required=False, default=False, type=bool, help='Force reinstallation of SteamCMD before running command(s)')
parser.add_argument('--mod-directory', '-m', metavar='DIR', type=isDir, required=True, help='Path to install mod(s) to')
parser.add_argument('--tool-directory', '-t', metavar='DIR', type=isDir, required=True, help='Path where steamcmd is installed')
parser.add_argument('--tool', '-T', required=True, choices=['steamcmd', 'depotdownloader'], help='Tool to use to download mods')
parser.add_argument('mods', metavar='mod ID', nargs='+', help='Mod ID(s) to download')

if len(sys.argv)==1:
    parser.print_help(sys.stderr)
    sys.exit(1)
args = parser.parse_args()

PPREFIX  		= f'[{os.path.basename(sys.argv[0])}]'
username        = args.username
app_id 			= args.app_id
batch 			= args.batch
refresh 		= args.refresh
mod_directory   = args.mod_directory
tool_directory  = args.tool_directory
home_directory  = str(pathlib.Path.home()) + '/'
steam_directory = home_directory + '.steam/'
tool            = args.tool
mods            = args.mods
password        = getpass.getpass(prompt=f'[{os.path.basename(sys.argv[0])}] Please enter Steam password for \'{username}\': ')

def refreshSteamCMD():
	print(PPREFIX, 'Removing & reinstalling SteamCMD')
	if not input(f'Are you sure? This will remove {steam_directory} and {tool_directory} - y/n: ').lower().strip()[:1] == "y": sys.exit(1)

	try:
		shutil.rmtree(tool_directory)
		print(PPREFIX, Fore.GREEN, f'Removed {tool_directory}')
	except:
		print(PPREFIX, Fore.RED, f'Failed to remove {tool_directory}')
		sys.exit(1)
	try:
		shutil.rmtree(steam_directory)
		print(PPREFIX, Fore.GREEN, f'Removed {steam_directory}')
	except:
		print(PPREFIX, Fore.RED, f'Failed to remove {steam_directory}')
		sys.exit(1)

	try:
		request.urlretrieve('https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz', home_directory + 'steamcmd.tar.gz')
	except:
		print(PPREFIX, Fore.RED, 'Failed to download SteamCMD archive')
		sys.exit(1)

	print(PPREFIX, 'Extracting SteamCMD archive')
	archive = tarfile.open(home_directory + 'steamcmd.tar.gz', 'r:gz')
	archive.extractall(tool_directory)

	print(PPREFIX, 'Removing SteamCMD archive')
	os.remove(home_directory + 'steamcmd.tar.gz')

if tool == 'steamcmd':
	if refresh:
		refreshSteamCMD()

	if batch:
		print(PPREFIX, f'Downloading/updating {len(mods)} mods')

		mod_str = f' +workshop_download_item {app_id} '.join(str(i)+' validate' for i in mods)
		command = f'{tool_directory}/steamcmd.sh +login {username} {password} +force_install_dir {mod_directory} +workshop_download_item {app_id} {mod_str} +quit'
		try:
			subprocess.run(command.split(sep=' '), stdout=None, check=True)
		except:
			print(PPREFIX, Fore.RED, 'Failed to download/update mod(s)')
			sys.exit(1)
	else:
		failed = []
		for i in range(len(mods)):
			print(PPREFIX, f'Downloading mod {i + 1} of {len(mods)} ({mods[i]})')

			path 	= mod_directory + mods[i]
			command = f'{tool_directory}/steamcmd.sh +login {username} {password} +force_install_dir {mod_directory} +workshop_download_item {app_id} {mods[i]} validate +quit'
			try:
				subprocess.run(command.split(sep=' '), stdout=None, check=True)
				print('\n\n' + PPREFIX, Fore.GREEN, f'Successfully downloaded mod {mods[i]}')
			except:
				print(PPREFIX, Fore.RED, f'Failed to download mod {mods[i]}')
				failed.append(mods[i])

		if len(failed):
			print(PPREFIX, Fore.RED, f'Failed to download {len(failed)} mods')
			for i in failed:
				print(i, end='')
elif tool == 'depotdownloader':
	for i in range(len(mods)):
		print(PPREFIX, f'Downloading mod {i + 1} of {len(mods)} ({mods[i]})')

		path 	= mod_directory + mods[i]
		command = f'dotnet {tool_directory}/DepotDownloader.dll -username {username} -password {password} -remember-password -dir {mod_directory} -app {app_id} -pubfile {mods[i]}'
		if subprocess.run(command.split(sep=' '), stdout=None, check=True):
			print(PPREFIX, Fore.GREEN, f'Successfully downloaded mod {mods[i]}')
		else:
			print(PPREFIX, Fore.RED, f'Failed to download mod {mods[i]}')
			sys.exit(1)