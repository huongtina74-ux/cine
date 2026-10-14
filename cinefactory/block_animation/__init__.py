from cinefactory.block_animation.contracts import EpisodeSpec,CompiledEpisode,BlenderAnimationJob
from cinefactory.block_animation.registry import BlockAnimationLibraries
__all__=['EpisodeAssembler','EpisodeSpec','CompiledEpisode','BlenderAnimationJob','BlockAnimationLibraries','ContinuousBlockFactory']
def __getattr__(name):
    if name=='EpisodeAssembler':
        from cinefactory.block_animation.assembler import EpisodeAssembler; return EpisodeAssembler
    if name=='ContinuousBlockFactory':
        from cinefactory.block_animation.factory import ContinuousBlockFactory; return ContinuousBlockFactory
    raise AttributeError(name)
