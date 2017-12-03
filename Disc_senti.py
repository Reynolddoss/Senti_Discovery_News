import sys
import os
import json
from watson_developer_cloud import DiscoveryV1
from datetime import timedelta, date,datetime
import config
class DiscoveryNewsSentimentAnalyzer(object):

    def _daterange(self, start_date, end_date):
        arr = []
        for n in range(int((end_date - start_date).days + 1)):
            arr.append(start_date + timedelta(n))
        return arr

    def get_sentiment_score(self, start_date, end_date):
        dates =  self._daterange(start_date, end_date)
        discovery = DiscoveryV1(
            username=config.discovery['username'],
            password=config.discovery['password'],
            version=config.discovery['version']
        )
        
        tot_score = 0
        tot_count =0
        for idx, elem in enumerate(dates):
            #print( single_date[i].strftime("%Y-%m-%d"))
            thiselem = elem
            nextelem = dates[(idx + 1) % len(dates)]
            date1 = thiselem.strftime("%Y-%m-%d")
            date2 = nextelem.strftime("%Y-%m-%d")
            filter ="language:(english|en),crawl_date>%sT12:00:00+0530,crawl_date<%sT12:00:00+0530"  % (date1, date2)
            qopts = {
                "query": "\"term to be searched\"",
                "filter": filter,
                "aggregations": [
                "term(host).term(enriched_text.sentiment.document)",
                "term(enriched_text.sentiment.document)"
                    ],
                'return': 'enriched_text.sentiment.document',
                'count': 50,
                'offset': 0
            }

            #print(qopts)
            matching_results=100000

            while True:
                if qopts['offset'] >= matching_results:
                    break
                my_query = discovery.query('system', 'news', qopts)
                matching_results=my_query['matching_results']
                for result in my_query['results']:
                    try:
                        label = result['enriched_text']['sentiment']['document']['label']
                        score = result['enriched_text']['sentiment']['document']['score']
                        #print("score",score)
                    except Exception as e:
                        label = "NO LABEL"
                        score = "NO SCORE"

                    tot_score += score
                    tot_count += 1
                qopts['offset'] = qopts['offset'] + 50

        return tot_score/tot_count

if __name__ == '__main__':
	discovery_sentiment =DiscoveryNewsSentimentAnalyzer()
	average_sentiment = discovery_sentiment.get_sentiment_score()
	print(average_sentiment)
