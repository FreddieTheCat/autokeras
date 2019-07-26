from tensorflow.python.util import nest

from autokeras.hypermodel import block, node
from autokeras.hypermodel import processor


class CompositeHyperBlock(block.HyperBlock):

    def build(self, hp, inputs=None):
        """Build the HyperModel instead of Keras Model."""
        raise NotImplementedError


class ImageBlock(CompositeHyperBlock):
    """HyperBlock for image data.

    The image blocks is a block choosing from ResNetBlock, XceptionBlock, ConvBlock,
    which is controlled by a hyperparameter, 'block_type'.

    # Arguments
        block_type: String. 'resnet', 'xception', 'vanilla'. The type of HyperBlock
            to use. If left unspecified, it will be tuned automatically.
    """

    def __init__(self, block_type=None, **kwargs):
        super().__init__(**kwargs)
        self.block_type = block_type

    def build(self, hp, inputs=None):
        input_node = nest.flatten(inputs)[0]
        output_node = input_node

        block_type = self.block_type or hp.Choice('block_type',
                                                  ['resnet', 'xception', 'vanilla'],
                                                  default='resnet')

        if block_type == 'resnet':
            output_node = block.ResNetBlock()(output_node)
        elif block_type == 'xception':
            output_node = block.XceptionBlock()(output_node)
        elif block_type == 'vanilla':
            output_node = block.ConvBlock().build(output_node)
        return output_node


class TextBlock(CompositeHyperBlock):

    def __init__(self, vectorizer=None, pretraining=None, **kwargs):
        super().__init__(**kwargs)
        self.vectorizer = vectorizer
        self.pretraining = pretraining

    def build(self, hp, inputs=None):
        input_node = nest.flatten(inputs)[0]
        output_node = input_node
        vectorizer = self.vectorizer or hp.Choice('vectorizer',
                                                  ['sequence', 'ngram'],
                                                  default='sequence')
        if not isinstance(input_node, node.TextNode):
            raise ValueError('The input_node should be a TextNode.')
        if vectorizer == 'ngram':
            output_node = processor.TextToNgramVector()(output_node)
            output_node = block.DenseBlock()(output_node)
        else:
            output_node = processor.TextToIntSequence()(output_node)
            output_node = block.EmbeddingBlock(
                pretraining=self.pretraining)(output_node)
            output_node = block.ConvBlock(separable=True)(output_node)
        return output_node


class StructuredDataBlock(CompositeHyperBlock):

    def build(self, hp, inputs=None):
        raise NotImplementedError


class TimeSeriesBlock(CompositeHyperBlock):

    def build(self, hp, inputs=None):
        raise NotImplementedError


class GeneralBlock(CompositeHyperBlock):
    """A general neural network block when the input type is unknown. """

    def build(self, hp, inputs=None):
        raise NotImplementedError
