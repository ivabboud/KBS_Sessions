from experta import *


class Car(Fact):
    pass


class UserChoice(Fact):
    pass


def cf_calculation(cf1, cf2):
    if cf1 >= 0 and cf2 >= 0:
        return cf1 + cf2 * (1 - cf1)
    if cf1 < 0 or cf2 < 0:
        return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))
    return cf1 + cf2 * (1 + cf1)


class Engine(KnowledgeEngine):

    @DefFacts()
    def init(self):
        yield Car(name='Car 1', CF=0, data={'high_price': 0.9, 'sport_car': 0.7, 'old_classic': 0.4}, done='False')
        yield Car(name='Car 2', CF=0, data={'high_price': 0.7, 'sport_car': 0.5, 'old_classic': 0.2}, done='False')
        yield Car(name='Car 3', CF=0, data={'high_price': 0.3, 'sport_car': 0.2, 'old_classic': 0.8}, done='False')

    @Rule(NOT(UserChoice(high_price=W())), salience=5)
    def ask_for_price(self):
        cf = input('Do you want to buy a high price car?')
        self.declare(UserChoice(high_price=cf))

    @Rule(NOT(UserChoice(sport_car=W())), salience=4)
    def ask_for_sport(self):
        cf = input('Do you want to buy a sport car?')
        self.declare(UserChoice(sport_car=cf))

    @Rule(NOT(UserChoice(old_classic=W())), salience=3)
    def ask_for_new(self):
        cf = input('Do you want to buy a classic car?')
        self.declare(UserChoice(old_classic=cf))
        self.declare(UserChoice('done'))

    @Rule(UserChoice(high_price=MATCH.high_price), UserChoice(sport_car=MATCH.sport_car),
          UserChoice(old_classic=MATCH.old_classic))
    def calc_results(self, high_price, sport_car, old_classic):
        results = []
        for factId in list(self.facts):
            if type(self.facts[factId]) is Car:
                total_cf = self.facts[factId]['CF']
                for k, v in self.facts[factId]['data'].items():
                    if k == 'high_price':
                        total_cf = cf_calculation(total_cf, v * float(high_price))
                    elif k == 'sport_car':
                        total_cf = cf_calculation(total_cf, v * float(sport_car))
                    elif k == 'old_classic':
                        total_cf = cf_calculation(total_cf, v * float(old_classic))

                results.append((self.facts[factId]['name'], total_cf))

        results = sorted(results, key=lambda x: x[1], reverse=True)
        print(results)


engine = Engine()
engine.reset()
engine.run()
