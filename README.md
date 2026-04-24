# Intelligent Budget Allocation System for Advertisment Campaigns
date: 2026/4/22\
version: 0.0.1\
author: Piotr Sziroky

---
## Table of Contents
- [Introduction](#introduction)
- [Rules & Principles](#rules___principles)
- [Problem Statement](#problem-statement)
- [Setup & Requirements](#setup--requirements)
- [Data Flow Diagram](#data-flow-diagram)
- [Architecture Overview](#architecture-overview)
- [Metrics & Evaluation](#metrics--evaluation)


## Introduction
Without oxygen there is no fire same as without money there is no campaigns. Just like fire if you want to cook over it you need to control how much wood you will use.\
If You are using too much you burned the stew and you just used a lot of wood for nothing and the opposite you are not giving the fire enough fuel you will lose the heat or in the worst case you end with just ashes.

This analogy I think its very good when it comes to advertisment campaigns. If we want to have successful campaigns we need to control how much money we allocate to each campaign and make sure that we are getting the best results. But honestly what does it means the best results?\

I think we are going to try solve it together. But I do not expect there is one single best truth.

## Rules & Principles
1. The Budget is limited to 85,000 USD weekly

The system i will build must follow these principles:
1. **Opportunity Cost**\
If this would be simple as "put money into the higher ROAS" there would be no need for inteligent system rather a *"if"* system.\
Yes, high ROAS indicates that we are getting more revenue but also we should look at different metrics.\
Why putting more money into high ROAS campaign that is not converting, the CPA is extremly low and audience is saturated.\
I think you can have high roas but at the same time the campaign is no longer "attracting" anyone so we need to keep in mind this is not an simple thing.

2. **Diversification vs Concentration**\
We can put all the budget into one efficient campaign or diverse the budget into new ones.\
The system will read the client instructions based on this will propose to allocate the budget the authors propose Herfindahl–Hirschman Index (wchich calculates the concentration of budget part among the campaignes).\
There is also an Threshold of 0.25 HHI that means we put a lot of trust in one advertisment platform the safest is to have a HHI 1/n (1/3 per platform since we operating on 3 platforms) but is it the smartest decision?\
We need to give the human-in-the-loop to make decision give him insights on how concentrated is the budget in this strategy what risk it has.

3. **Risk Menagment**
#### Volatility
Marketing like the stock its more about tommorow than today. thats why we need to carefully look at the trend. This makes total sense you can have two campaign, same ROAS but different trend and that it pitting money in one that generate more cosst than revenue simply don't make sense.
#### Platform Concentration
No single platform should receive more than 55% of total budget unless the output explicitly justifies the exception. Breaching this threshold is a risk, not a default
#### Minimum viable spend
The money we can put into campaign is limited from the bottom level. This is represent by min_viable_spend in the data. We should flag if the mininimum is not met and recomend to stop it completly not to put money that statistacly doesnt make any sense. 


## Problem Statement 
First I need to understand what Im dealing with.\
From what I can find in the campaingns data (campaigns.json) I see:

### Marketing Indices

- *ROAS - Return of Ad Spend*:\
In other terms how much we spend vs how much ad revenue we get.\
To calculate we will use simple $ROAS = \frac{revenue}{spend}$.\
Higher Roas we get the campaign is more feasible.

- *CPA - Cost Per Action*:\
This metric describe the cost of user performing action an specific action.\
This cost shows the real cost of making the user perform a specific action.

- *Conversion Volume*:\
The number of conversions that occurred during the period campaign was active (assumption!).\
A conversion can be defined as the rate of turning user to an customer using the advertisment.

- *Audience Saturation Signal*\
A metric decribing how much the audience is familiar (in worst case fatigue) with the campaign.\
Basically if higher it means the campaign is more likely to get less clicks and conversions.\
Roughly said: it's getting boring. 

### Trend Data

- *4 Weeks ROAS Trend:*\
This metric describes if the ROAS is increasing, decreasing or flat over the last 4 weeks.

### Descriptive Fields

- *Campaign ID*\
Name of the campaign.

- *Platform*\
Platform of the campaign (Google, Meta, TikTok)

- *Campaign Type*\
The type of the campaign (retargeting, brand, prospecting)

### Financial Fields

- *Current Weekly Spend*\
The amount of weekly spend budget.

- *Platform Level Budget Cap*\
The maximum budget that can be spent on this platform.

- *Minimum Viable Spend*\
The minimum amount of money that needs to be spent in order for the campaign to be viable.

Based on this information I've created a Pydantic model `core/models.py` that  represents the input data and will help me dealing with the data in the future (f.e generating new sets of data or in production validate if the data are not corrupted).

But now let's talk about system

## System Overview

Let's talk what this system will be and won't be whats the major risks and major cappabilities.

### What it will be?
Im thinking about human in the loop recomendation system since we deal with the money we need to have either highly reliable and densly evaluated system or have a human to decide. Of course we should give the "operator" as much insight, strategies or plans as possible. We will analyze the data and the connection between them as well as the client brief note. This note can have incostinces and ambigouity so we will need to give LLM insights about the past campaign data. The system should recognize the risk and provide flags, warnings and recommendations. 

The system should be evaluated with Eval Harness layer here are some of the criterion:
- **Allocation accuracy**: within ±10% of ground-truth spend per campaign 
- **Action agreement**: does the system agree on scale/hold/reduce/pause? 
- **Risk flag recall**: did the system catch the same risk flags a human identified? 
- **Total budget constraint**: hard fail if total ≠ $85,000 

### The flow of the system:
The flow of this function is as follows:
    1. Load the campagn data and parse it into objects.
    2. Create initial campaign data profiles using statistics (z-scores) and descriptive categories (for LLM).
    3. Send the initial profiles into LLM and ask to analyze the strategy brief based on that fill the LLM-origin fields in the profiles (priorities, rationale, strategy).
    4. Based on the statistical and LLM insights we will allocate the budget but deterministically not stochastically.
    5. We Create a list of Campaings that are not paused.
    6. We sort the list based on pririties assigned by the LLM.
    7. We allocate the minimum spend of each campagn and check if not exceed 85,000 budget.
    8. If we are we drop the last campaign and check the rest (Not ideal and not preffered approach)
    9. We then have a list of campaigns and their budget allocations.
    10. We calculate how much part of the 85 grant we give to each campaign.
        Formula:
        ((Weight ROAS z-score) - (Weight CPA z-score) + (Weight * (1 - Saturation))) * (LLM Priority) * (ROAS Trend Multiplier)
    11. Evaluation of the final result allocation

## Results

Unfortunatelly, The system is not ready yet it orchestrate a i designed but there are critical errors within it i want to recognize and fix in future. The main issue is that the evaluation is not correct so each case is different. Why its not working propably bedcause the formula to allocate the budget was creatively invented and not based on any research 

To be continued...
