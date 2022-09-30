This commit is only to archive the Yaz compression algorithm I wrote.

The next commit will completely remove the 'filelib' package from this project.
Why? Because the compression algorithm is too slow to be actually useful.
Compressing a U8 archive of average length takes over 5 minutes. For reference,
my algorithm written in C++ (which can be found in narahiero/CTLib on GitHub)
takes 1.5 seconds to compress that same archive.

I do not have the necessary knowledge of Python to write an algorithm that would
compress within a reasonable amount of time.

From now on, the purpose of this add-on will be to export the necessary data
from the Blender file and run an external program written in C++ which will then
create a file usable by the Wii.
