# drink-182
A machine that makes cocktails 

### Features
 - Can make a large variety of cocktails using only 3 alcoholic drinks (vodka, rum, gin) and 5 mixers (cola, lemonade, limeade, orangeade, tropicalade)
 - Displays the ABV and number of units per cocktail
 - Touchscreen support for easy selection
 - Admin menu accessable using a password allowing the tweaking of various settings
 - Substitution system, liquids can have replacements given (i.e. substitute orange juice for orangeade if needed)

### Requirements
 - Raspberry Pi (I used the Pi 3) and some sort of touchscreen for it
 - Some sort of arduino with at least 8 digital output pins (I used the Uno)
 - An 8-channel optocoupler
 - 8 normally closed solenoid valves
 - An AC/DC power supply
 - A 5V to 12V buck converter, although this depends on the voltage required by your solenoid valves
 - A fair few sheets of wood or some material to make it out of (I used MDF)

### The Software

![screenshot of selection screen](https://raw.githubusercontent.com/Lumorti/drink-182/master/images/ui_selection.png)

![screenshot of make screen](https://raw.githubusercontent.com/Lumorti/drink-182/master/images/ui_make.png)

### The Circuit

![circuit plan](https://raw.githubusercontent.com/Lumorti/drink-182/master/images/circuit_plan.png)

### The Panels

![wood cutting plan](https://raw.githubusercontent.com/Lumorti/drink-182/master/images/mdf_plan.png)

