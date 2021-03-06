
from elo import FRCElo
from knockout_predictor import KnockoutPredictor
import pickle
import statistics
import math

default_stdev = 50

elo = FRCElo(qm_K=20, fm_K=5, new_team_rating=1350, init_stdev=default_stdev)

briers = []
year_briers = []

predictions_outcomes = []

i = 0

for year in range(2008, 2018):
    with open("../cache/" + str(year) + "matches.p", "rb") as year_file:
        year_events = pickle.load(year_file)
        processed_teams = []
        for event_code, event in year_events.items():
            for match_num, match in enumerate(event):

                forecast = elo.predict(match)
                processed_match = FRCElo.get_match_data(match)
                margin = processed_match.blue_score - processed_match.red_score
                outcome = 0.5 if margin == 0 else (1 if margin > 0 else 0)

                if year % 2 == 0:
                    predictions_outcomes.append((forecast, outcome))
                    briers.append((forecast - outcome) ** 2)

                elo.update(match)

                if (match['comp_level'] == 'qm'
                        and not event[match_num+1]['comp_level'] == 'qm'):
                    alliance_data = self.tba_wrapper.fetch_alliance_data(self.event.event_code)
                    # also add a condition to ensure that the event is efs
                    # predict the knockouts
                    pass

        if not briers == []:
            print("%s year brier %s" % (year, statistics.mean(briers)))
            year_briers.append(statistics.mean(briers))
        briers = []
        elo.next_year(1500, 0.2, default_stdev)

print(statistics.mean(year_briers))

num_buckets = 10

predict_buckets = [0 for i in range(num_buckets)]
outcome_buckets = [0 for i in range(num_buckets)]

for match in predictions_outcomes:
    bucket_num = math.floor(match[0] * num_buckets)
    predict_buckets[bucket_num] += 1
    outcome_buckets[bucket_num] += match[1]

calibration_score = 0
for i, num_predictions, num_outcomes in zip(
        range(0, num_buckets), predict_buckets, outcome_buckets):
    bucket_mean = ((i * 10) + 5) / 100
    print("%s - %s - %s"
          % (bucket_mean, num_outcomes / num_predictions, num_predictions))
    calibration_score += abs(bucket_mean - (num_outcomes / num_predictions))

print(calibration_score)

blue_wins = 0
red_wins = 0
for match in predictions_outcomes:
    if match[1] == 0:
        red_wins += 1
    elif match[1] == 1:
        blue_wins += 1

print("red: %s, blue %s" % (red_wins, blue_wins))
