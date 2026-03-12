# fixed-point

* Fixed-Point is a pytest plugin designed to record and replay deterministic function calls, making your tests stable and reproducible.
* Flaky tests are the bane of every developer's existence. I prefer not to rely on retries, mocks that drift from reality, or fragile test setups to keep things green.
* To tackle this problem, Fixed-Point captures real function outputs and replays them faithfully, so your tests always land on the same answer — a fixed point.
* It boasts simplicity, making it exceptionally easy to adopt in any pytest project.
* Fixed-Point serves as a specialized testing tool, particularly tailored for pinning down the behavior of functions that talk to external services. If you encounter any cases not covered by the plugin, please don't hesitate to create an issue for further assistance.

## Installation

You can install pytest-fixedpoint using pip, the Python package manager:

```
pip install pytest-fixedpoint
```

## Getting Started

To start using fixed-point in your project, simply use the fixture in your tests:

```python
from fixedpoint import fixed_point

def test_my_function(fixed_point):
    result = fixed_point(my_function, "arg1", "arg2")
    assert result == expected  # first run records, subsequent runs replay
```

## Why fixed-point?

* Today I want to dedicate something to my beloved wife, and I'm eager to make it meaningful.
* I've created this open-source project called "Fixed-Point," because she is my fixed point — always cute, always kind, and forever constant no matter how chaotic the world gets.
* In mathematics, a fixed point is a value that remains unchanged by a function. She is exactly that — the one thing in my life that is steady, warm, and unchanging.
* The package is named "fixed-point" because, just like in math, some things converge to a beautiful, stable truth. She is mine.
* This project is designed to bring stability to tests the same way she brings stability to my life — quietly, reliably, and with grace.
* With this, I hope to bring a smile to her face, and maybe to yours too.
