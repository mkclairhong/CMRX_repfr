# CMRX_repfr
Modified version of CMR (Context Maintenance and Retrieval Model) to simulate retrieval practice effects 


Despite broad success reproducing many repetition effects with CMR, Lohnas et al's (2014) simulations substantially underpredicted the magnitude of the spacing effect observable in their data. At first glance this gap may be explicable in terms of authors' decision not to fit the model directly to their dataset. However, even when I replicate their simulations using a version of the model with parameters fit directly to their dataset, I found that CMR fails \textt{to the same extent} to identify a large increasing difference in recall probabilities for items with presentations spaced 1-2, 3-5, or 6-8 positions from one another. These results suggest that even as CMR realizes the encoding variability and study-phase retrieval accounts of the spacing effect, it cannot fully account for the full effect observable in behavioral data.

For this project, let's 
1. concretize and explain this apparent gap, 
2. specify and analyze ways to integrate deficient processing into CMR to enable an improved composite account of spacing and repetition effects in free recall, and 
3. try to generate novel predictions about the dynamics of free recall based on how CMR-DE works.

## Getting Started

I've been using `nbdev` to organize my Python projects. Basically, `nbdev` includes commands for converting selected cells across collections of Jupyter Notebooks into a Python module library, documentation, and set of tests.

Every cell in the notebooks located at the root of this directory with an `# export` comment at the top of them are included in the library within the module indicated by the `# defaultexp` comment at the top of those notebooks.

You can just use each notebook as a reference or tutorial if you'd rather not take the trouble to figure out how to use this library. That is, you can clone this repo and peruse notebooks and copy code based on what you're trying to do. Just stick your work inside the `workspace/` subdirectory to keep it from being integrated into the broader library. If you have any problems pushing, just share the code some other way (e.g. with Google Drive or by Slack).

If you'd like to use `repfr` as a library, clone this repository and at its root execute the command `pip install -e .`. Once you do this, Python code executed in the same environment can import a module from repfr (e.g. `from repfr.models import DefaultCMR`) and then use it without re-specifying any code.

In general, we'll use notebooks in the root directory to specify our shared library of functionality. Code in the workspace directory will contain more project-specific analyses and works-in-progress.

If you have any issues using any of this code, just let me know! It's still very much a work in progress.
