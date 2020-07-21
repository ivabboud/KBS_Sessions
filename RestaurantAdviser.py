from experta import *


class Restaurant(Fact):
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
    def initial_fact(self):
        yield Restaurant(name='A', CF=0, meals=['B', 'L'], stars=2,
                         data={'western': 0.7, 'eastern': 0.9, 'family': 0.6, 'work': 0.2, 'date': 0.5}, proc='False')
        yield Restaurant(name='B', CF=0, meals=['B', 'L', 'D'], stars=4,
                         data={'western': 0.1, 'eastern': 0.8, 'family': 0.8, 'work': 0.7, 'date': 0.1}, proc='False')
        yield Restaurant(name='C', CF=0, meals=['B', 'L', 'D'], stars=3,
                         data={'western': 0.9, 'eastern': 0.1, 'family': 0.5, 'work': 0.2, 'date': 0.9}, proc='False')
        yield Restaurant(name='D', CF=0, meals=['L', 'D'], stars=1,
                         data={'western': 0.5, 'eastern': 0.5, 'family': 0.9, 'work': 0.1, 'date': 0.1}, proc='False')

        # A Test Case
        # yield UserChoice(meal='B')
        # yield UserChoice(eastern=0.9)
        # yield UserChoice(western=0.2)
        # yield UserChoice(min_stars=3, max_stars=5)
        # yield UserChoice(family=0.9)
        # yield UserChoice(work=0.2)
        # yield UserChoice(date=0.3)

    @Rule(NOT(UserChoice(meal=W())), salience=5)
    def ask_for_meal(self):
        self.declare(UserChoice(meal=input('What do you want to eat? B-L-D ')))

    @Rule(NOT(UserChoice(eastern=W())), salience=4)
    def ask_for_eastern(self):
        self.declare(UserChoice(eastern=float(input('Would you like to eat Eastern Food?'))))

    @Rule(NOT(UserChoice(western=W())), salience=4)
    def ask_for_western(self):
        self.declare(UserChoice(western=float(input('Would you like to eat Western Food?'))))

    @Rule(NOT(UserChoice(min_stars=W())), salience=3)
    def ask_for_stars(self):
        min_stars = int(input('What is the Minimum Stars of the restaurant you want me to suggest?: '))
        max_stars = int(input('What is the Maximum Stars of the restaurant you want me to suggest?: '))
        self.declare(UserChoice(min_stars=min_stars, max_stars=max_stars))

    @Rule(NOT(UserChoice(family=W())))
    def ask_for_occasion_f(self):
        self.declare(UserChoice(family=float(input('Do you want the restaurant for a Family occasion?: '))))

    @Rule(UserChoice(family=MATCH.family), NOT(UserChoice(work=W())))
    def ask_for_work(self, family):
        if family < 0.8:
            self.declare(UserChoice(work=float(input('Do you want the restaurant for a Work occasion?: '))))
        else:
            self.declare(UserChoice(work=0))

    @Rule(UserChoice(work=MATCH.work), NOT(UserChoice(date=W())))
    def ask_for_date(self, work):
        if work < 0.8:
            self.declare(UserChoice(date=float(input('Do you want the restaurant for your Date?: '))))
        else:
            self.declare(UserChoice(date=0))

    # to loop over all the restaurant facts
    @Rule(AS.fact << Restaurant(CF=MATCH.CF, meals=MATCH.meals, data=MATCH.data, stars=MATCH.stars, proc='False'),
          UserChoice(family=MATCH.family), UserChoice(work=MATCH.work), UserChoice(date=MATCH.date),
          UserChoice(meal=MATCH.meal),
          TEST(lambda meal, meals: meal in meals),
          UserChoice(min_stars=MATCH.min_stars), UserChoice(max_stars=MATCH.max_stars),
          TEST(lambda min_stars, max_stars, stars: min_stars <= stars <= max_stars))
    def calculate_results(self, f, data, family, work, date):
        cf_total = 0
        for k, v in data.items():
            if k == 'family':
                cf_total = cf_calculation(cf_total, family * v)
            elif k == 'work':
                cf_total = cf_calculation(cf_total, work * v)
            elif k == 'date':
                cf_total = cf_calculation(cf_total, date * v)

        self.modify(f, CF=cf_total, proc='True')

    # Another way to loop over the facts
    @Rule(NOT(Fact('done')), salience=-1)
    def get_results(self):
        results = []
        for factId in list(self.facts):
            if type(self.facts[factId]) is Restaurant:
                results.append((self.facts[factId]['name'], self.facts[factId]['CF']))

        # Sorting the result Descending
        results = sorted(results, key=lambda x: x[1], reverse=True)
        print(results)
        self.declare(Fact('done'))


engine = Engine()
engine.reset()
engine.run()
