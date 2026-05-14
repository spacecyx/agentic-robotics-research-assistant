# Query Expansion
# 作用：基于规则生成多个 query variants，提高召回率

from __future__ import annotations


class HeuristicQueryExpander:
    """
    轻量规则版 Query Expansion。

    目标：
    1. 不依赖 LLM
    2. 不依赖网络
    3. 针对论文 RAG 常见问题做术语扩展
    4. 为后续 LLM Query Rewriter 预留接口
    """

    def __init__(self):
        self.rules: list[tuple[list[str], list[str]]] = [
            (
                ["degradation", "deeper plain", "plain network", "training error"],
                [
                    "degradation problem higher training error not caused by overfitting",
                    "deep plain networks optimization difficulty training accuracy degrades",
                ],
            ),
            (
                ["residual learning", "residual", "h(x)", "f(x)", "mapping"],
                [
                    "residual learning reformulates H(x) as F(x)+x where F(x)=H(x)-x",
                    "residual function identity mapping shortcut connection",
                ],
            ),
            (
                ["shortcut", "skip connection", "identity"],
                [
                    "identity shortcut connections add no extra parameter or computational complexity",
                    "shortcut connections identity mapping residual blocks",
                ],
            ),
            (
                ["projection", "match dimensions", "dimension"],
                [
                    "projection shortcut Ws x match dimensions 1x1 convolution",
                    "dimensions increase projection shortcuts option B option C",
                ],
            ),
            (
                ["bottleneck", "resnet-50", "resnet-101", "resnet-152"],
                [
                    "bottleneck design 1x1 3x3 1x1 reducing increasing dimensions",
                    "deeper bottleneck architectures ResNet-50 ResNet-101 ResNet-152",
                ],
            ),
            (
                ["experiment", "experimental", "results", "imagenet", "cifar"],
                [
                    "ImageNet classification top-1 top-5 error ResNet-152 validation test",
                    "CIFAR-10 ResNet training error test error 110-layer 1202-layer",
                ],
            ),
            (
                ["limitation", "limitations", "overfitting"],
                [
                    "1202-layer ResNet overfitting test error worse than 110-layer",
                    "aggressively deep models open problems overfitting small dataset",
                ],
            ),
            (
                ["object detection", "faster r-cnn", "coco", "pascal"],
                [
                    "Faster R-CNN ResNet-101 VGG-16 COCO mAP object detection",
                    "PASCAL VOC COCO detection ResNet learned representations",
                ],
            ),
            (
                ["training strategy", "train", "optimization", "sgd"],
                [
                    "batch normalization SGD momentum weight decay learning rate ImageNet training",
                    "training schedule mini-batch weight initialization no dropout",
                ],
            ),
            (
                ["attention", "transformer", "self-attention"],
                [
                    "scaled dot-product attention query key value softmax sqrt dk",
                    "multi-head attention representation subspaces different positions",
                ],
            ),
        ]

    def expand(
        self,
        query: str,
        max_queries: int = 4,
    ) -> list[str]:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        query = " ".join(query.strip().split())
        lower_query = query.lower()

        query_variants = [query]

        for triggers, expansions in self.rules:
            if any(trigger in lower_query for trigger in triggers):
                query_variants.extend(expansions)

        query_variants = self._deduplicate(query_variants)

        return query_variants[:max_queries]

    @staticmethod
    def _deduplicate(queries: list[str]) -> list[str]:
        seen = set()
        deduped = []

        for query in queries:
            key = query.lower().strip()

            if key in seen:
                continue

            seen.add(key)
            deduped.append(query)

        return deduped