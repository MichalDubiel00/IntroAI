This repository contains a PIP package which is an OpenAI environment for
simulating an wumpusworld and fuzzy-cartpole environment.


## Installation

Install the [OpenAI gym](https://github.com/openai/gym).
Read The manual [OpenAI manual](https://www.gymlibrary.ml).

Then install this package via

```
pip install -e .
```

## Usage

```
import gym
import fh_ac_ai_gym

wumpus_env = gym.make('Wumpus-v0')
cartpole_env = gym.make('Fuzzy-CartPole-v0')
```


The wumpus action space is containing the following actions:

```
   WALK = 0
   TURNLEFT = 1
   TURNRIGHT = 2
   GRAB = 3
   SHOOT = 4
   CLIMB = 5
```

The fuzzy env is taking the applied force +/- to the cart as action.
For the cartpole env you have to use .step_with_(force) instead of the step(action)


```
   obs, reward,done, info = env.step_with_(cart.output['force'])
```

