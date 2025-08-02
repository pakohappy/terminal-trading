# Utils Directory

This directory contains utility modules for the trading system, particularly focused on the standardized robot creation framework.

## Directory Structure

- **base/**: Contains the base classes for robots
  - `robot_base.py`: The base class that all robot implementations inherit from
  - `__init__.py`: Package initialization file that exports RobotBase

- **robots/**: Contains specific robot implementations
  - `robot_stochastic.py`: Implementation of a trading robot using the Stochastic Oscillator
  - `robot_triple_sma.py`: Implementation of a trading robot using Triple Simple Moving Averages
  - `robot_advanced.py`: Implementation of an advanced trading robot combining Triple SMA and Alligator
  - `__init__.py`: Package initialization file that exports all robot classes

- **factory/**: Contains factory classes for creating robot instances
  - `robot_factory.py`: Factory class that simplifies the creation of different types of robots
  - `__init__.py`: Package initialization file that exports RobotFactory

## Usage

To use the robot framework, you can import the necessary classes from their respective modules:

```python
# Import the base class
from utils.base import RobotBase

# Import specific robot implementations
from utils.robots import StochasticRobot, TripleSMARobot, AdvancedRobot

# Import the factory for easier robot creation
from utils.factory import RobotFactory

# Create a robot using the factory
robot = RobotFactory.create_robot('stochastic', symbol='EURUSD')
```

See the main README_ROBOTS.md file for more detailed usage instructions.