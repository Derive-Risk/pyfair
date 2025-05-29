Calculation Details
===================

The nodes can be described as follows:

**Risk ("R")**
--------------

Description
~~~~~~~~~~~
A vector of currency values/elements, which represent the ultimate loss
for a given time period

Restrictions
~~~~~~~~~~~~
All elements must be positive

Derivation
~~~~~~~~~~
Multiply the Loss Event Frequency vector by the Loss Magnitude vector

.. math::

    \begin{bmatrix}
        \text{R}_{1} \\
        \text{R}_{2} \\
        \vdots \\
        \text{R}_{m}
    \end{bmatrix}
    =
    \begin{bmatrix}
        \text{LEF}_{1} \\
        \text{LEF}_{2} \\
        \vdots \\
        \text{LEF}_{m}
    \end{bmatrix}
    \times
    \begin{bmatrix}
        \text{LM}_{1} \\
        \text{LM}_{2} \\
        \vdots \\
        \text{LM}_{m}
    \end{bmatrix}

Example
~~~~~~~
For a given year, if we have the number of times a particular event
occurs (Loss Event Frequency/LEF) and the dollar losses associated with
each of those events (Loss Magnitude/LM), we can multiply these
together to derive the ultimate dollar value amount lost (Risk/R).

+------------+-----+--------+--------------+
| Simulation | LEF | LM     | R (LEF x LM) |
+============+=====+========+==============+
| 1          | 100 | $1,000 | $100,000     |
+------------+-----+--------+--------------+
| 2          | 100 | $2,000 | $200,000     |
+------------+-----+--------+--------------+
| 3          | 200 | $3,000 | $600,000     |
+------------+-----+--------+--------------+

**Loss Event Frequency ("LEF")**
--------------------------------

Description
~~~~~~~~~~~
A vector of elements which represent the number of times a particular
loss occurs during a given time frame (generally one year)

Restrictions
~~~~~~~~~~~~
All elements must be positive

Derivation
~~~~~~~~~~
Supplied directly, or multiply the Threat Event Frequency vector by the
Vulnerability vector

.. math::

    \begin{bmatrix}
        \text{LEF}_{1} \\
        \text{LEF}_{2} \\
        \vdots \\
        \text{LEF}_{m}
    \end{bmatrix}
    =
    \begin{bmatrix}
        \text{TEF}_{1} \\
        \text{TEF}_{2} \\
        \vdots \\
        \text{TEF}_{m}
    \end{bmatrix}
    \times
    \begin{bmatrix}
        \text{V}_{1} \\
        \text{V}_{2} \\
        \vdots \\
        \text{V}_{m}
    \end{bmatrix}

Example
~~~~~~~
For a given year, if we have the number of times a particular threat
occurs (Threat Event Frequency/TEF), and the percentage of times we can
expect that threat to turn into a loss (Vulnerability/V), we can
multiply these together to derive the number of losses that will occur
(Loss Event Frequency/LEF).

+------------+------+------+---------------+
| Simulation | TEF  | V    | LEF (TEF x V) |
+============+======+======+===============+
| 1          | 0.50 | 0.50 | 0.25          |
+------------+------+------+---------------+
| 2          | 200  | 0.25 | 50            |
+------------+------+------+---------------+
| 3          | 300  | 1.00 | 300           |
+------------+------+------+---------------+

.. note::

    Though intended to represent a discrete number of events, TEF and
    LEF are not rounded to the nearest integer. This allows for
    the modeling of events that happen infrequently. For instance, if
    we are running a simulation for a single year, one might model a
    once a century occurrence using a LEF/TEF of 0.01.

**Threat Event Frequency ("TEF")**
----------------------------------

Description
~~~~~~~~~~~
A vector of elements representing the number of times a particular
threat occurs, whether or not it results in a loss

Restrictions
~~~~~~~~~~~~
All elements must be positive

Derivation
~~~~~~~~~~
Supplied directly, or multiply the Contact Frequency vector and the
Probability of Action vector

.. math::

    \begin{bmatrix}
        \text{TEF}_{1} \\
        \text{TEF}_{2} \\
        \vdots \\
        \text{TEF}_{m}
    \end{bmatrix}
    =
    \begin{bmatrix}
        \text{C}_{1} \\
        \text{C}_{2} \\
        \vdots \\
        \text{C}_{m}
    \end{bmatrix}
    \times
    \begin{bmatrix}
        \text{A}_{1} \\
        \text{A}_{2} \\
        \vdots \\
        \text{A}_{m}
    \end{bmatrix}

Example
~~~~~~~
For a given year, if we have the number of times an actor comes in
contact with an asset (Contact Frequency/C), and the probability that
the actor will attempt to act of that contact (Probability of Action,
P), we can multiply these together to derive the number of times that
a particular threat will occur (Threat Event Frequency/TEF)

+------------+-------+------+---------------+
| Simulation | C     | A    | TEF (C x A)   |
+============+=======+======+===============+
| 1          | 1,000 | 0.50 | 500           |
+------------+-------+------+---------------+
| 2          | 2,000 | 0.25 | 500           |
+------------+-------+------+---------------+
| 3          | 3,000 | 1.00 | 3,000         |
+------------+-------+------+---------------+

**Vulnerability ("V")**
-----------------------

Description
~~~~~~~~~~~
A vector of elements with each value representing the probability that
a potential threat actually results in a loss

Restrictions
~~~~~~~~~~~~
All elements must be from 0.0 to 1.0

Derivation
~~~~~~~~~~
Supplied directly, or via the following operation:

.. math::

    \bar{V}
    \;
    \text{Where}
    \;
    V_{i}
    =
    \begin{cases}
        1, & \text{if} \; \text{TC}_{i} \; \geq \text{CS}_{i}\\
        0, & \text{if} \; \text{TC}_{i} \; \lt \text{CS}_{i}\\
    \end{cases}

Or in more concrete terms, we have a vector of Threat Capabilities and
a vector of Control Strengths. For each element of the vector, we
determine if Threat Capability is greater than Control Strength. In
other words, 1 is where the threat overwhelms the control, and 0 is
where the control withstands the threat.

.. math::

    \text{TC}
    =
    \begin{bmatrix}
        0.60 \\
        0.70 \\
        0.10 \\
    \end{bmatrix}
    \quad
    \text{CS}
    =
    \begin{bmatrix}
        0.55 \\
        0.65 \\
        0.75 \\
    \end{bmatrix}
    \quad
    \overrightarrow{Indicator Function}
    \quad
    \text{Intermediate}
    =
    \begin{bmatrix}
        1 \\
        1 \\
        0 \\
    \end{bmatrix}

We then analyze this intermediate array of ones and zeros, and obtain
its average. The represents the percent of times in our simulations
that the threat overcame the control.

.. math::

    \text{Intermediate}
    =
    \begin{bmatrix}
        1 \\
        1 \\
        0 \\
    \end{bmatrix}
    \quad
    \overrightarrow{Average}
    \quad
    \frac
        {(1 + 1 + 0)}
        {3}
    =
    0.66

This scalar is then assigned to a vector for the sake of computational
consistency.

.. math::

    \text{V}
    =
    \begin{bmatrix}
        0.66 \\
        0.66 \\
        0.66 \\
    \end{bmatrix}

Example
-------
For a given year, if we have the relative strengths of attackers
(Threat Capability/TC) and the relative strengths of our controls
(Control Strength/CS), we can run a step function and then average the
result to obtain a percentage of times we expect a threat to overcome
a control (Vulnerability/V).

+------------+------+------+------+
| Simulation | TC   | CS   | V    |
+============+======+======+======+
| 1          | 0.60 | 0.50 | 0.33 |
+------------+------+------+------+
| 2          | 0.10 | 0.50 | 0.33 |
+------------+------+------+------+
| 3          | 0.30 | 0.40 | 0.33 |
+------------+------+------+------+

.. note::

    For the purposes of this calculation, TC must be estimated relative
    to CS, and CS must be estimated relative to TC. They are
    essentially just rough guesses to determine the percentage of
    threats that will fail or succeed (and consequently have no
    independent meaning apart from each other).

**Contact Frequency ("C")**
---------------------------

Description
~~~~~~~~~~~
A vector with elements representing the number of threat
actor contacts that could potentially yield a threat within a given
timeframe

Restrictions
~~~~~~~~~~~~
All elements must be a positive number

Derivation
~~~~~~~~~~
None (this must be supplied, not calculated)

Example
~~~~~~~
For a given year, the number of contacts that can potentially yield an
attack, and in turn can potentially yield a loss (Contact Frequency/C).

+------------+-----------+
| Simulation | C         |
+============+===========+
| 1          | 5,000,000 |
+------------+-----------+
| 2          | 3,000,000 |
+------------+-----------+
| 3          | 2,500,000 |
+------------+-----------+

**Probability of Action ("A")**
-------------------------------

Description
~~~~~~~~~~~
A vector with elements representing the probability that a threat actor
will proceed after coming into contact with an organization

Restrictions
------------
All elements must be number from 0.0 to 1.0

Derivation
----------
None (this must be supplied, not calculated)

Example
-------
The probability that a contact results in action being taken against a
resource (Probability of Action/P)

+------------+------+
| Simulation | P    |
+============+======+
| 1          | 0.95 |
+------------+------+
| 2          | 0.90 |
+------------+------+
| 3          | 0.80 |
+------------+------+

**Threat Capability ("TC")**
----------------------------

Description
~~~~~~~~~~~
A vector of unitless elements that describe the relative
level of expertise and resources of a threat actor (relative to a
Control Strength)

Restrictions
~~~~~~~~~~~~
All elements must be number from 0.0 to 1.0

Derivation
~~~~~~~~~~
None (this must be supplied, not calculated)

Example
-------
The relative strength of a threat actor (Threat Capability/C) as it
relates to the relative strength of the controls (Control Strength/CS)

+------------+------+
| Simulation | TC   |
+============+======+
| 1          | 0.75 |
+------------+------+
| 2          | 0.60 |
+------------+------+
| 3          | 0.70 |
+------------+------+

**Control Strength ("CS")**
---------------------------

Description
~~~~~~~~~~~
A vector of unitless elements that describe the relative strength of a
given control (relative to the Threat Capability of a given actor)

Restrictions
~~~~~~~~~~~~
All elements must be a number from 0.0 to 1.0

Derivation
~~~~~~~~~~
None (this must be supplied, not calculated)

Example
-------
The relative strength of a set of controls (Control Strength/CS) as it
relates to the relative strength of a threat actor (Threat
Capability/TC)

+------------+------+
| Simulation | TC   |
+============+======+
| 1          | 0.15 |
+------------+------+
| 2          | 0.10 |
+------------+------+
| 3          | 0.05 |
+------------+------+

**Loss Magnitude ("LM")**
-------------------------

Description
~~~~~~~~~~~
A vector of currency values describing the total loss for a single Loss
Event

Restrictions
~~~~~~~~~~~~
All elements must be positive

Derivation
~~~~~~~~~~
Supplied directly, or the sum of the Primary Loss vector and Secondary
Loss vector

.. math::

    \begin{bmatrix}
        \text{LM}_{1} \\
        \text{LM}_{2} \\
        \vdots \\
        \text{LM}_{m}
    \end{bmatrix}
    =
    \begin{bmatrix}
        \text{PL}_{1} \\
        \text{PL}_{2} \\
        \vdots \\
        \text{PL}_{m}
    \end{bmatrix}
    +
    \begin{bmatrix}
        \text{SL}_{1} \\
        \text{SL}_{2} \\
        \vdots \\
        \text{SL}_{m}
    \end{bmatrix}

Example
~~~~~~~
For a given loss, if we have the total dollar amount of a primary loss
(Primary Loss/PL), and the total dollar amount of a secondary loss
(Secondary Loss/SL), we can obtain the total amount (Loss Magnitude/LM)
by adding PL and SL.

+------------+------+-----+--------------+
| Simulation | PL   | SL  | LM (PL + SL) |
+============+======+=====+==============+
| 1          | $120 | $80 | $200         |
+------------+------+-----+--------------+
| 2          | $210 | $5  | $215         |
+------------+------+-----+--------------+
| 3          | $200 | $60 | $260         |
+------------+------+-----+--------------+

**Primary Loss ("PL")**
-----------------------

Description
~~~~~~~~~~~
A vector of currency losses directly attributable to the threat

Restrictions
~~~~~~~~~~~~
All elements must be positive

Derivation
~~~~~~~~~~
None (this must be supplied, not calculated)

Example
~~~~~~~
The amount of the loss directly attributable to the threat (Primary
Loss/PL)

+------------+------------+
| Simulation | PL         |
+============+============+
| 1          | $5,000,000 |
+------------+------------+
| 2          | $3,500,000 |
+------------+------------+
| 3          | $2,500,000 |
+------------+------------+

**Secondary Loss ("SL")**
-------------------------

Description
~~~~~~~~~~~
A vector of currency losses attributable to secondary factors

Restrictions
~~~~~~~~~~~~
All elements must be positive

Derivation
~~~~~~~~~~
Supplied directly, or the rowwise sum of 1) the Secondary Loss Event
Frequency vector and 2) the Secondary Loss Event Magnitude vector
multiplied together on an elementwise basis.

.. math::

    \\begin{split}
        \\mathbf{SL} &=
        \\sum_{j=1}^{n} \\left( \\mathbf{SLEF} \\circ \\mathbf{SLEM} \\right)_{rowwise} \\\\
        \\text{where:} \\\\
        \\mathbf{SLEF} &=
        \\begin{bmatrix}
                \\text{SLEF}_{1,1} & \\text{SLEF}_{1,2} & \\dots  & \\text{SLEF}_{1,n} \\\\
                \\text{SLEF}_{2,1} & \\text{SLEF}_{2,2} & \\dots  & \\text{SLEF}_{2,n} \\\\
                \\vdots            & \\vdots            & \\ddots & \\vdots \\\\
                \\text{SLEF}_{m,1} & \\text{SLEF}_{m,2} & \\dots  & \\text{SLEF}_{m,n}
        \\end{bmatrix} \\\\
        \\mathbf{SLEM} &=
        \\begin{bmatrix}
                \\text{SLEM}_{1,1} & \\text{SLEM}_{1,2} & \\dots  & \\text{SLEM}_{1,n} \\\\
                \\text{SLEM}_{2,1} & \\text{SLEM}_{2,2} & \\dots  & \\text{SLEM}_{2,n} \\\\
                \\vdots            & \\vdots            & \\ddots & \\vdots \\\\
                \\text{SLEM}_{m,1} & \\text{SLEM}_{m,2} & \\dots  & \\text{SLEM}_{m,n}
        \\end{bmatrix} \\\\
        \\mathbf{SL} &=
        \\begin{bmatrix}
                \\text{SL}_{1} \\\\
                \\text{SL}_{2} \\\\
                \\vdots        \\\\
                \\text{SL}_{m}
        \\end{bmatrix}
    \\end{split}

Example
~~~~~~~
For a given model, we can have a matrix of secondary loss
probabilities. Each row can represent a simulation and each column can
represent a loss type. In this example below we have three different
probability columns for different types of probability loss. E.g. the
probabilities of loss for simulation 1 are 0.95, 0.05, and 1.00.

+------------+-------------+--------------+--------------+
| Simulation | Prob Loss A | Prob Loss B  | Prob Loss C  |
+============+=============+==============+==============+
| 1          | 0.95        | 0.05         | 1.00         |
+------------+-------------+--------------+--------------+
| 2          | 0.90        | 0.10         | 1.00         |
+------------+-------------+--------------+--------------+
| 3          | 0.50        | 0.10         | 0.80         |
+------------+-------------+--------------+--------------+

For a given model, we can also have the dollar amounts associated with
these individual loss types.

+------------+-------------+--------------+--------------+
| Simulation | $ Loss A    | $ Loss B     | $ Loss C     |
+============+=============+==============+==============+
| 1          | $1,000      | $100         | $50          |
+------------+-------------+--------------+--------------+
| 2          | $2,000      | $50          | $90          |
+------------+-------------+--------------+--------------+
| 3          | $1,500      | $30          | $25          |
+------------+-------------+--------------+--------------+

This allows us to match up these matrices on an element-by-element
basis and say something like:

Cell 1A from table 1 is 0.95 and cell 1A from table 2 is $1,000.
Multiplying (Sim 1, Prob Loss A) by (Sim 1, $ Loss A) yields $950. We
can put this result in table 3.

+------------+------------------+
| Simulation | Secondary Loss A |
+============+==================+
| 1          | $950             |
+------------+------------------+

If we do this for every cell in tables 1 and 2, we can a new table that
has the secondary losses for each loss type and each simulation.

+------------+--------+--------+--------+
| Simulation | SL (A) | SL (B) | SL (C) |
+============+========+========+========+
| 1          | $950   | $5     | $50    |
+------------+--------+--------+--------+
| 2          | $1,800 | $5     | $90    |
+------------+--------+--------+--------+
| 3          | $750   | $3     | $20    |
+------------+--------+--------+--------+

Finally, it is possible to add up each row to get the total amount of
Secondary Loss for a given simulation. This Secondary Loss vector can
then be added to the Primary Loss vector to do further calculations.

+------------+----------------------+
| Simulation | Total Secondary Loss |
+============+======================+
| 1          | $1,005               |
+------------+----------------------+
| 2          | $1,895               |
+------------+----------------------+
| 3          | $773                 |
+------------+----------------------+

**Secondary Loss Event Frequency ("SLEF")**
-------------------------------------------

Description
~~~~~~~~~~~
A matrix of probabilities with each row representing a single
simulation, and each column represents the probability that a
particular secondary loss type will occur

Restrictions
------------
All matrix elements must be number from 0.0 to 1.0

Derivation
----------
None (this must be supplied, not calculated)

Example
~~~~~~~
For a given model, you may have three simulations and three separate
different loss types. This would give you three different probabilities
for each simulation, and three different simulations for each
probability type.

+------------+-------------+--------------+--------------+
| Simulation | Prob Loss A | Prob Loss B  | Prob Loss C  |
+============+=============+==============+==============+
| 1          | 0.95        | 0.05         | 1.00         |
+------------+-------------+--------------+--------------+
| 2          | 0.90        | 0.10         | 1.00         |
+------------+-------------+--------------+--------------+
| 3          | 0.50        | 0.10         | 0.80         |
+------------+-------------+--------------+--------------+

**Secondary Loss Event Magnitude ("SLEM")**
-------------------------------------------

Description
~~~~~~~~~~~
A matrix of currency amounts with each row representing a single
simulation, and each column represents the the amount of loss for amount
particular loss type

Restrictions
------------
All matrix elements must be positive

Derivation
----------
None (this must be supplied, not calculated)

Example
~~~~~~~
For a given model, you may have three simulations and three separate
different loss types. This would give you three different dollar
amounts for each simulation, and three different simulations for each
dollar amount type.

+------------+-------------+--------------+--------------+
| Simulation | $ Loss A    | $ Loss B     | $ Loss C     |
+============+=============+==============+==============+
| 1          | $1,000      | $100         | $50          |
+------------+-------------+--------------+--------------+
| 2          | $2,000      | $50          | $90          |
+------------+-------------+--------------+--------------+
| 3          | $1,500      | $30          | $25          |
+------------+-------------+--------------+--------------+
