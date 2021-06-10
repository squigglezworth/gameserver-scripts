#!/bin/python3
import os, argparse, sys, shutil, subprocess, glob, time

mods = [
450814997,       # CBA
463939057,       # ACE
1376867375,      # ACE Menu Expansion
708250744,       # ACEX
333310405,       # Enhanced Movement
2034363662,      # Enhanced Movement Rework

# 721359761,       # VCOM AI
# 1858075458,      # LAMBS Danger
# 1858070328,      # LAMBS RPG
# 1808238502,      # LAMBS Suppression
# 1862208264,      # LAMBS Turrets

583496184,       # CUP Terrains - Core
583544987,       # CUP Terrains - Maps
541888371,       # CUP Vehicles
497660133,       # CUP Weapons
549676314,       #    ACE compatibility
497661914,       # ^ CUP Units

843577117,       # RHS USAF
773125288,       #   ACE Compatibility
#843425103,      # RHS AFRF
#773131200,      #   ACE Compatibility
#843593391,      # RHS GREF
#884966711,      #   ACE Compatibility
#843632231,      # RHS SAF
#2174495332,     #    ACE Compatibility

1779063631,      # ZEN
2018593688,      # ZEN ACE Compatibility

639837898,       # Advanced Towing
713709341,       # Advanced Rappelling
730310357,       # Advanced Urban Rappelling
615007497,       # Advanced Sling Loading

1862880106,      # POLPOX's Base Functions (Dependency)
1997001841,      # Plane Loadout Everywhere

313041182,       # NVGs (L3-GPNVG18)
1224892496,      # GRAD Trenches
1388192893,      # ITC Land Systems
1803586009,      # Faster Ladders
820924072,       # BackpackOnChest
281074849,       # Fluid/Incremental Door Opening
1199318917,      # Vehicle-in-Vehicle Loading
1113616706,      # US Patches & Emblems
#949252631,      # Aegis
#2176977109,     # Spiritus Systems Equipment
#753946944,      # Cigarettes
#1660226023,      # Task Force Canada

823636749,       # VSM
1974559189,      # VSM ACE Compatibility
2127190744,      # Moe Pilot Gear Suite

787892271,       # Firewill A-10 Warthog
366425329,       # Firewill AWS

#784218341,       # The Mighty GAU-8
#2172110674,     #    USAF Compatibility
#949704851,       #    RHS Compatibility
#949701797,       #    Firewill Compatibility
#949699485,       #    CUP Compatibility
#949698441,       #    ACE Compatibility

#2397371875,     # USAF Fighters
#2397360831,     # USAF Main
#2397376046,     # USAF Utility

#1523363834,     # HAFM Core
#1118982882,     # HAFM Navy
#1362114638,     # HAFM Submarine
]

def isDir(path):
	if os.path.isdir(path):
		return path.rstrip('/')
	else:
		raise argparse.ArgumentTypeError(f"{path} is not a valid path")

def renameFiles(mods):
	path = mod_dir + '/steamapps/workshop/content/107410/'

	# Python sucks, long live the CLI!
	os.system(f"find {path} -depth -type d -name '*[A-Z]*' -exec rename 'y/A-Z/a-z/' {{}} \;")
	os.system(f"find {path} -depth -type f -name '*[A-Z]*' -exec rename 'y/A-Z/a-z/' {{}} \;")
	print('')

def moveKeys(mods):
	for mod in mods:
		path = mod_dir + '/steamapps/workshop/content/107410/' + str(mod) + '/'
		for f in glob.glob(path + '**/*.bikey', recursive=True):
			# print('Copying {} to {}'.format(f, f'/home/squigz/arma/keys/{os.path.basename(f)}'))
			# sys.exit(1)
			if shutil.copy(f, f'/home/squigz/arma/keys/{os.path.basename(f)}'):
				print('.', end='')
			else:
				print(PPREFIX, f'Failed to move key(s) for {mod}')
				sys.exit(1)
	print('')

parser = argparse.ArgumentParser(description='Manage an arma server', add_help=False)
parser.add_argument('--tool-directory', '-t', metavar='DIR', type=isDir, required=True, help='Path where Steam tool is located - see moddownloader.py -h for options')
parser.add_argument('--mod-directory', '-m', metavar='DIR', type=isDir, required=True, help='Path to install mod(s) to')
parser.add_argument('--arma-directory', '-a', metavar='DIR', type=isDir, required=True, help='Path where arma server files are located')
parser.add_argument('--username', '-u', help='Steam username for downloading/updating mods')
parser.add_argument('--cleanup', '-c', help='Cleanup cache')
parser.add_argument('action', choices=['start', 'update', 'download', 'rename', 'keys', 'permissions'], help='Action to perform on the server')

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

PPREFIX   = f'[{os.path.basename(sys.argv[0])}]'
APP_ID    = 107410
args      = parser.parse_args()
action    = args.action
username  = args.username
arma_dir  = args.arma_directory
mod_dir   = args.mod_directory
tool_dir  = args.tool_directory

if action == 'update' or action == 'download':
	if not username:
		parser.error(PPREFIX + 'Please provide a username (--username/-u)')

	print(PPREFIX, 'Downloading/updating {} mods...'.format(len(mods)))

	mod_str = ' '.join(str(i) for i in mods)
	command = f'python3 moddownloader.py -u {username} -m {mod_dir} -T steamcmd -t {tool_dir} -a {APP_ID} {mod_str}'
	try:
		subprocess.run(command.split(sep=' '), check=True)
	except:
		print(PPREFIX, 'Failed to download/update mod(s)')
		sys.exit(1)()

	print('\n\n' + PPREFIX, 'Successfully installed/updated mod(s)', end='')
	time.sleep(5)

	if action == 'update':
		print('\n' + PPREFIX, 'Moving key(s)', end='')
		moveKeys(mods)

	if action == 'update':
		print('\n' + PPREFIX, 'Renaming files', end='')
		renameFiles(mods)
elif action == 'rename':
	print(PPREFIX, 'Renaming files', end='')

	renameFiles(mods)
elif action == 'keys':
	print(PPREFIX, 'Moving key(s)', end='')

	moveKeys(mods)
elif action == 'permissions':
	print(PPREFIX, 'Updating permissions', end='')

	fixPermissions(mods)
elif action == 'start':
	print(PPREFIX, 'Starting server...')

	os.chdir(arma_dir)
	command = './arma3server_x64 -ip=135.148.76.38 -noPause -noSound -loadMissionToMemory -world=empty -config={}/server.cfg -mod="mods/{}" -enableHT'.format(arma_dir, ';mods/'.join(str(i) for i in mods))
	print(command)
	# sys.exit(1)
	# subprocess.run(command.split(sep=' '), cwd=arma_dir, check=True)
	os.system(command)