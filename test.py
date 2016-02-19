#!/usr/bin/python
import json
import requests

import settings
import redis




def test():
    payload = {
        u'food': [[3, 1], [15, 4], [18, 13], [13, 4], [12, 17]],
        u'game': u'halting-humility',
        u'gold': [[10, 10]],
        u'height': 20,
        u'mode': u'advanced',
        u'snakes': [{
            u'age': 15,
            u'coords': [[0, 15], [1, 15], [2, 15]],
            u'gold': 0,
            u'health': 85,
            u'id': u'ee925ec8-01f4-4f08-a05d-617a97cad866',
            u'kills': 0,
            u'message': u'',
            u'name': u'Sendwithus',
            u'status': u'alive',
            u'taunt': u''
        },{
            u'age': 15,
            u'coords': [[4, 0], [4, 1], [4, 2]],
            u'gold': 0,
            u'health': 85,
            u'id': u'3d2f2b54-6c65-402f-b1ea-75b72d2ccbfb',
            u'kills': 0,
            u'message': u'',
            u'name': u'Trump Snake',
            u'status': u'alive',
            u'taunt': u'My net worth is many, many times that of Sendwithus'}],
        u'turn': 15,
        u'walls': [],
        u'width': 20
     }
     
    start_url = "http://localhost:5000/start"
    r = requests.post(start_url, json.dumps(payload))

if __name__ == '__main__':
    test()

# move_url = "http://localhost:5000/move"
# r = requests.post(move_url, json.dumps(move_payload))
# print r

# for distance in range(0, 10):
#     head = Node(move_payload, "A")
#     (move, score, node) = head.best_move(distance)
#     print "looking %s moves ahead, my best score is: %s, %s" % (distance, score, move)