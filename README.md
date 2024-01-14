# WOOFenstein

WOOFenstein is a working implementation of a Ray-caster engine. The main inspiration was the engine of Wolfenstein 3D.

## Launching WOOFenstein

To play the game, follow these simple steps:

1. **Clone this Repository:**
   ```bash
   git clone https://github.com/Szyntos/WOOFenstein.git
   
2. **Install Dependencies:**

    Ensure you have Python and pip installed. Install the required dependencies by running:

    ```bash
    pip install -r requirements.txt
    ```
3. **Run the Game:**

    Start the game by executing the main.py file:

    ```bash
    python main.py
    ```



## Game Instructions
1. **Enemies are pathfinding to you when you're not looking at them**
   
   They are following a path that is designated by the visibility graph of the map.
2. **You can shoot them!**
   
   Each enemy has 10 HP - shoot them till they die.
3. **You have 1HP**

   Don't lose it.
4. **Collect all rainbow objectives**
5. **Have Fun!**

## Game Options

1. **Check the options:**

   You can change mouse sensitivity and the playable map (you can choose demo / mainGame or maze).
   
2. **Check config.json:**

   Changing config.json is needed to change fov, window size and map size. 

## Creating a new map

To create a new map run editor.py:

 ```bash
 python editor.py
 ```

The map you'll be editing is map.json. 
 
- Placing or selecting an object - left mouse button.
- Resizing an object - arrow keys
- Moving an object - W A S D
- Cycling through object types - ',' and '.' (comma and full_stop)
- Saving an object and whole map - space
- Deleting an object - backspace

## Game Demo

![demo.gif](https://raw.githubusercontent.com/Szyntos/WOOFenstein/main/demo.gif)

## Requirements

- numpy==1.24.3

- perlin-noise==1.12

- pygame==2.4.0

- pyvisgraph==0.2.1

- shapely==2.0.1

- tqdm==4.65.0
- 
## Contributors
* [Szymon Nowak-Trzos](https://github.com/Szyntos/)
* [Mateusz Zając](https://github.com/MagrosThornrime)
