#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import difflib


class RecommendationFinder:

    def __init__(self, normalizer=None):
        self.normalizer = normalizer or (lambda x: x)

    def find_and_format(self, name, candidates, message, max_matches=10):
        recommendations = self.find(name, candidates, max_matches)
        return self.format(message, recommendations)

    def find(self, name, candidates, max_matches=10):
        """Return a list of close matches to `name` from `candidates`."""
        if not name or not candidates:
            return []
        norm_name = self.normalizer(name)
        norm_candidates = self._get_normalized_candidates(candidates)
        cutoff = self._calculate_cutoff(norm_name)
        norm_matches = difflib.get_close_matches(
            norm_name, norm_candidates, n=max_matches, cutoff=cutoff
        )
        return self._get_original_candidates(norm_matches, norm_candidates)

    def format(self, message, recommendations):
        """Add recommendations to the given message.

        The recommendation string looks like::

            <message> Did you mean:
                <recommendations[0]>
                <recommendations[1]>
                <recommendations[2]>
        """
        if recommendations:
            message += " Did you mean:"
            for rec in recommendations:
                message += "\n    %s" % rec
        return message

    def _get_normalized_candidates(self, candidates):
        norm_candidates = {}
        for cand in sorted(candidates):
            norm = self.normalizer(cand)
            norm_candidates.setdefault(norm, []).append(cand)
        return norm_candidates

    def _get_original_candidates(self, norm_matches, norm_candidates):
        candidates = []
        for match in norm_matches:
            candidates.extend(norm_candidates[match])
        return candidates

    def _calculate_cutoff(self, string, min_cutoff=0.5, max_cutoff=0.85, step=0.03):
        """Calculate a cutoff depending on string length.

        Default values determined by manual tuning until the results "look right".
        """
        cutoff = min_cutoff + len(string) * step
        return min(cutoff, max_cutoff)
