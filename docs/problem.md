# Problem statement

## The problem

Quick-commerce apps show an item price, but what a shopper pays is the item price plus a delivery fee, a handling fee and sometimes a small-cart fee, each with its own thresholds. The cheapest sticker price is often not the cheapest order. Checking properly means building the same cart in three apps and reading three checkout screens, which few people do for a ₹60 purchase.

There is also a second trade-off that the apps do not help with: a platform that is a few rupees cheaper may deliver noticeably later, and whether that is worth it depends on the shopper and the moment.

## Who it is for

People in Indian cities who order groceries from more than one quick-commerce app and want to know, before opening any of them, which one is best for what they need right now.

## What PriceSense AI does about it

1. Works out the all-in total on each platform, with every fee applied.
2. Ranks platforms by the shopper's stated priority: lowest price, fastest, or balanced.
3. Explains the recommendation in one or two sentences, including what the shopper gives up by taking it.
4. Does the same for a whole basket, flags items a platform cannot supply, and suggests splitting the order when that saves a meaningful amount.

## What it is not (yet)

This repository is a working prototype on sample data. It does not fetch live prices; the platforms do not provide public APIs for that. See the Data section of the README for what a production version would need.
