# Neat Cars

## 📝 Description

Neat cars allows you to draw a track, a starting point and then let the magic happen. The cars will drive themselves and constantly improve their driving skills. The project is based on an evolutionary algorithm called [NEAT (NeuroEvolution of Augmenting Topologies)](https://en.wikipedia.org/wiki/Neuroevolution_of_augmenting_topologies).

## 🎥 Demo

### Track 1

https://user-images.githubusercontent.com/52708150/222574922-a3c87cc1-4c62-4ef6-8fbf-e140916e2571.mp4

### Track 2

https://user-images.githubusercontent.com/52708150/222576430-46c42039-3349-4336-80d0-2ad643bdf972.mp4

## 💡 How to use

### Prerequisites

* Python 3.7.0+

Get a copy of the Project. Assuming you have git installed, open your Terminal and enter:

```bash
git clone 'https://github.com/marcpinet/neat-cars.git'
```

To install all needed requirements run the following command in the project directory:

```bash
pip install -r requirements.txt
```

### Running

After that, you can proceed to start the program by running `main.py`.

### Controls and tweaks

Instructions are displayed in the window's title.

![title](https://i.imgur.com/ikz1mq5.png)

You can also see the stats of the current generation in the title...

![title2](https://i.imgur.com/foaowFK.png)

...and the full stats inside the console.

![console](https://i.imgur.com/TuNHLf4.png)

Feel free to tweak the parameters inside the `ai/config.txt` but also the static variables inside the `Car`, `Car_AI` and `Engine` classes.
For example, you can disable the rendering if the car's sensors by setting `DRAW_SENSORS` to `False` in the `Car` class.

## 🐛 Known issues

* The cars can get stuck in an infinite turn (the algorithm will still fixes itself while evolving tho)

## 🥅 TO-DO List

* Add a checkpoint system to allow 8-like tracks
* Improve the reward system of the evolutionary algorithm

## ✍️ Authors

* **Marc Pinet** - *Initial work* - [marcpinet](https://github.com/marcpinet)

## 📃 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
