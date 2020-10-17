class NewOffers:
    @staticmethod
    def diff(new_offers, old_offers, domain, user):
        try:
            if user.dealer == False and domain == 'otomoto.pl':
                offers_without_dealers = []
                for i, new_offer in enumerate(new_offers):
                    if new_offer['id'] == old_offers[0]['id']:
                        return offers_without_dealers
                    elif len(new_offer['dealer']) == 2: #jeśli dwa to znaczy ze jest puste chuj wie czemu
                        offers_without_dealers.append(new_offer)
                else:
                    return offers_without_dealers

            else:
                for i, new_offer in enumerate(new_offers):
                    if new_offer['id'] == old_offers[0]['id']:
                            return reversed(new_offers[0:i])

                else:
                    return new_offers

        except Exception as e:
            print(e)
            if user.dealer == False and domain == 'otomoto.pl':
                offers_without_dealers = []
                for new_offer in new_offers:
                    if len(new_offer['dealer']) == 2:
                        offers_without_dealers.append(new_offer)
                return offers_without_dealers
            else:
                return new_offers




