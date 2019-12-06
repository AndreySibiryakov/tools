import pysvn
import pyperclip


commit_message = 'Updated fxgraph mocap blink suppresion while playing lipsync'

destination_animsets_dir = 'c:/SVN/content/facefx/chrs/'
client = pysvn.Client()
commit_info = client.checkin(
    destination_animsets_dir, commit_message)
revision = str(commit_info).split(' ')[-1][:-1]
pyperclip.copy(revision)
print '# Commited at revision', revision
print '# Revision number copied to clipboard.'
