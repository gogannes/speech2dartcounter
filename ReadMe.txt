-----------------------------------------------------------------------
------------------------ Speech 2 DartCounter ------------------------- 
-----------------------------------------------------------------------

Version: Development (27 Oct 2020)

1. Open https://dartcounter.net/ in separate window and start a game (x01
   or singles training). 
   Open it only once! 
   Make sure the score text box is active.

2. Test whether window is detected by clicking on 'check window' button. 
   The window will be put in foreground, but it may take some time."

3. Click 'start' and play.

4. Speak your points following the syntax: 'a*b + c*d + e*f points', 
   where a-f are numbers.
   Don't forget the keyword 'points'.
   Don't pause inbetween or before the keyword 'points'.
   
   - Example DE: '3 mal 18 plus 3 und 5 Punkte' = 3*18+3+5
   - Example EN: '1 and 5 plus 60 Points' = 1+5+60
   - Example IT: '180 Punti' = 180

5. If a popup shows up during the game, you can close it with "okay"/"enter"

6. If necessary play with the threshold slider:
   - lower threshold: speach is detected and analyzed even if the microphone 
     signal is weak (good if you don't have a lot noise around).
   - higher threshold: good for a noisy environment, but you have to speak 
     directly into the microphone.

For nerds:
- 'Record:' shows the duration of the audio recording (it restarts periodically 
  after 3 sec, but continues if the threshold is reached.
- 'Google:' in case the threshold had been reached, the audio is transcribed 
  by google. The duration for the analysis is shown. For a smooth experience 
  it should be below 1 sec.

Developed by Johannes (gogannes@gmail.com).