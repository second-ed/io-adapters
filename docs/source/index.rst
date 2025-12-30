io-adapters documentation
=============================

Motivation
----------

Testing use cases that involve I/O is inherently difficult because they depend on external state and side effects. However, combining Dependency Injection (DI) with the Repository pattern significantly reduces this complexity.

By substituting real I/O implementations with fakes that simulate their behaviour, stateful interactions can be captured entirely in memory. This allows changes to the external world to be accumulated deterministically and the final state to be asserted directly, without relying on real filesystems, networks, or services.

The result is faster, more reliable tests that focus on behaviour rather than infrastructure.

However, creating these fakes can be time consuming and result in a maintenance burden that may not outweigh the benefit. 

This is where ``io-adapters`` can help. Simply register each I/O function with one of the register decorators and the functionality will be added to the ``RealAdapter`` object, on top of that a stub will be added to the ``FakeAdapter`` object too so you can pass in either to your usecase and the functionality will work.

.. automodule:: io-adapters
    :members:
    :undoc-members:
    :imported-members:
    :show-inheritance:

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`