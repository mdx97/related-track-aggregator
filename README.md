# Spotify Related Track Aggregator

A Python program for quickly collecting tracks from related artists on Spotify.

## Dependencies

You can install all the dependencies with pip.

```pip install -r requirements.txt```

## Configuration

You will need to create a Client ID and Client Secret on Spotify, and put those into your `config.json`. You will also need to whitelist a redirect uri (you can just use something on localhost).

## How to Use

```python3 aggregator.py <artist id>```

You can play around with the constants in the aggregator.py file if you wish to get different results.

## Unit Tests

Tests can be ran using the `unittest` module.

```python3 -m unittest aggregator_test.py```