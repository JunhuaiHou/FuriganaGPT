import threading


class Moderator:
    def __init__(self, gpt_client):
        self.gpt_client = gpt_client

    def moderate(self, pairs, results, index):
        violations = []
        for pair in pairs:
            prompt = pair[0]
            moderation_result_0 = self.gpt_client.client.moderations.create(input=prompt)

            if moderation_result_0.results[0].flagged:
                violations.append(prompt)
                continue

            answer = pair[1]
            moderation_result_1 = self.gpt_client.client.moderations.create(input=answer)

            if moderation_result_1.results[0].flagged:
                violations.append(answer)

        results[index] = violations

    def get_violations(self, training_pairs):
        len_total_training_pairs = len(training_pairs)
        quarter_point = len_total_training_pairs // 4
        results = [[] for _ in range(4)]

        pairs_parts = [
            training_pairs[:quarter_point],
            training_pairs[quarter_point:quarter_point * 2],
            training_pairs[quarter_point * 2:quarter_point * 3],
            training_pairs[quarter_point * 3:]
        ]

        threads = []

        for i in range(4):
            thread = threading.Thread(
                target=self.moderate,
                args=(pairs_parts[i], results, i)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return results[0] + results[1] + results[2] + results[3]