Input parameters for the cluster
===================================

The ``omnia.yml`` playbook is dependent on the inputs provided to the following input files:

* ``input/project_default/omnia_config.yml``
* ``input/project_default/security_config.yml``
* ``input/project_default/storage_config.yml``

.. caution:: Do not remove, edit, or comment any lines in the above mentioned input files.

``input/project_default/omnia_config.yml``
--------------------------------------------

.. csv-table:: Parameters for kubernetes setup
   :file: ../../../Tables/scheduler_k8s_rhel.csv
   :header-rows: 1
   :keepspace:

.. csv-table:: Parameters for slurm setup
   :file: ../../../Tables/scheduler_slurm.csv
   :header-rows: 1
   :keepspace:

``input/project_default/security_config.yml``
------------------------------------------------

.. csv-table:: Parameters for Authentication
   :file: ../../../Tables/security_config.csv
   :header-rows: 1
   :keepspace:

.. csv-table:: Parameters for OpenLDAP configuration
   :file: ../../../Tables/security_config_ldap.csv
   :header-rows: 1
   :keepspace:

.. csv-table:: Parameters for FreeIPA configuration
   :file: ../../../Tables/security_config_freeipa.csv
   :header-rows: 1
   :keepspace:


``input/project_default/storage_config.yml``
-----------------------------------------------

.. csv-table:: Parameters for Storage
   :file: ../../../Tables/storage_config.csv
   :header-rows: 1
   :keepspace:


Click here for more information on `OpenLDAP, FreeIPA <BuildingCluster/Authentication.html>`_, `BeeGFS <BuildingCluster/Storage/BeeGFS.html>`_, or `NFS <BuildingCluster/Storage/NFS.html>`_.

.. note::

    * The ``input/project_default/omnia_config.yml`` and ``input/project_default/security_config.yml`` input files are encrypted during the execution of ``omnia.yml`` playbook. Use the below commands to edit the encrypted input files:

        * ``omnia_config.yml``: ::

            ansible-vault edit omnia_config.yml --vault-password-file .omnia_vault_key

        * ``security_config.yml``: ::

            ansible-vault edit security_config.yml --vault-password-file .security_vault.key