import threading


class Moderator:
    def __init__(self, gpt_client):
        self.gpt_client = gpt_client
        self.moderation_results = []

    def get_scores(self, input, index):
        moderation_result = self.gpt_client.client.moderations.create(input=input)

        highest_score = max(vars(moderation_result.results[0].category_scores).values())
        self.moderation_results[index].append((input, moderation_result.results[0].flagged, highest_score))

    def moderate(self, pairs, index):
        for pair in pairs:
            self.get_scores(pair[0], index)
            self.get_scores(pair[1], index)

    def get_violations(self, training_pairs):
        len_total_training_pairs = len(training_pairs)
        fifth_point = len_total_training_pairs // 5
        self.moderation_results = [[] for _ in range(5)]

        pairs_parts = [
            training_pairs[:fifth_point],
            training_pairs[fifth_point:fifth_point * 2],
            training_pairs[fifth_point * 2:fifth_point * 3],
            training_pairs[fifth_point * 3:fifth_point * 4],
            training_pairs[fifth_point * 4:]
        ]

        threads = []

        for i in range(5):
            thread = threading.Thread(
                target=self.moderate,
                args=(pairs_parts[i], i)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return sum(self.moderation_results, [])
