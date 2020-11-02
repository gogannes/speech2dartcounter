-----------------------------------------------------------------------
------------------------ Speech 2 DartCounter ------------------------- 
-----------------------------------------------------------------------

Version: Development (27 Oct 2020)

Short instruction:
1. Open https://dartcounter.net/ in separate window and start a game (x01
   or singles training). 
   Open it only once!
   Make sure the score text box is active.

2. Click 'start' and play.

3. Speak your points following the syntax: 'a*b + c*d + e*f points',
   where a-f are numbers.
   Don't forget the keyword 'points'.
   Don't pause inbetween or before the keyword 'points'.
   
   - Example DE: '3 mal 18 plus 3 und 5 Punkte' = 3*18+3+5
   - Example EN: '1 and 5 plus 60 Points' = 1+5+60
   - Example IT: '180 Punti' = 180

Good to know:
-  If a popup shows up during the game, you can close it with "okay"/"enter".
   For the "darts used on double"-popup you can also say "0/1/2/3 Points" and
   the respective number is selected before it is closed.

-  You can set how often the "enter"-key is invoked after the score is typed
   in ("No. of enters").
   Recommendation:
   - x01 game: 2 (in case the "darts used on double" popup shows up, it will
     is closed immediately)
   - singles training game: 0

-  You can say "undo/rückgängig/anullare" to undo the last entered points
   (only working properly for x01-games)

-  If necessary play with the threshold slider:
   - lower threshold: speech is detected and analyzed even if the microphone
     signal is weak (good if you don't have a lot noise around).
   - higher threshold: good for a noisy environment, but you have to speak 
     directly into the microphone.
   - If 'Record' runs for more than 3 seconds even if you haven't spoken
     you have to increase the threshold! (your speech is only analyzed after
     the record is done)

For nerds:
- 'Record:' shows the duration of the audio recording (it restarts periodically 
  after 3 sec, but continues if the threshold is reached.
- 'Google:' in case the threshold had been reached, the audio is transcribed 
  by google. The duration for the analysis is shown. For a smooth experience 
  it should be below 1 sec.
- File 'languages.json': here most of the language settings are stored. The
  file can be changed in an editor and is read at program start

Developed by Johannes (gogannes@gmail.com).