import re


class TestListHostGraph:
	def test_no_hosts(self, host, add_host):
		"Test when no hosts are specified"

		result = host.run('stack list host graph')
		assert result.rc == 0
		assert re.match(r"""
			frontend-0-0\s+ digraph\ rocks\ {\s+
			frontend-0-0\s+	size="100,100";\s+
			frontend-0-0\s+ 	rankdir=LR;\s+
			frontend-0-0\s+ 	subgraph\ clusterkey\ {\s+
			frontend-0-0\s+ 		label="Rolls";\s+
			frontend-0-0\s+ 		fontsize=32;\s+
			frontend-0-0\s+ 		color=black;\s+
			frontend-0-0\s+ 	}\s+
			frontend-0-0\s+ 	subgraph\ clusterorder\ {\s+
			frontend-0-0\s+ 		label="Ordering\ Contraints";\s+
			frontend-0-0\s+ 		fontsize=32;\s+
			frontend-0-0\s+ 		color=black;\s+
			frontend-0-0\s+ 		(?:[^;}]+;\s+)+
			frontend-0-0\s+ 	}\s+
			frontend-0-0\s+	subgraph\ clustermain\ {\s+
			frontend-0-0\s+ 		label="Profile\ Graph";\s+
			frontend-0-0\s+ 		fontsize=32;\s+
			frontend-0-0\s+ 		color=black;\s+
			frontend-0-0\s+ 		(?:[^;}]+;\s+)+
			frontend-0-0\s+ 	}\s+
			frontend-0-0\s+ }\s+
			backend-0-0\s+ digraph\ rocks\ {\s+
			backend-0-0\s+	size="100,100";\s+
			backend-0-0\s+ 	rankdir=LR;\s+
			backend-0-0\s+ 	subgraph\ clusterkey\ {\s+
			backend-0-0\s+ 		label="Rolls";\s+
			backend-0-0\s+ 		fontsize=32;\s+
			backend-0-0\s+ 		color=black;\s+
			backend-0-0\s+ 	}\s+
			backend-0-0\s+ 	subgraph\ clusterorder\ {\s+
			backend-0-0\s+ 		label="Ordering\ Contraints";\s+
			backend-0-0\s+ 		fontsize=32;\s+
			backend-0-0\s+ 		color=black;\s+
			backend-0-0\s+ 		(?:[^;}]+;\s+)+
			backend-0-0\s+ 	}\s+
			backend-0-0\s+	subgraph\ clustermain\ {\s+
			backend-0-0\s+ 		label="Profile\ Graph";\s+
			backend-0-0\s+ 		fontsize=32;\s+
			backend-0-0\s+ 		color=black;\s+
			backend-0-0\s+ 		(?:[^;}]+;\s+)+
			backend-0-0\s+ 	}\s+
			backend-0-0\s+ }
		""", result.stdout, re.VERBOSE)

	def test_with_specific_host(self, host, add_host):
		"Test when a host is specified"
		
		result = host.run('stack list host graph backend-0-0')
		assert result.rc == 0
		assert re.match(r"""
			digraph\ rocks\ {\s+
				size="100,100";\s+
			 	rankdir=LR;\s+
			 	subgraph\ clusterkey\ {\s+
			 		label="Rolls";\s+
			 		fontsize=32;\s+
			 		color=black;\s+
			 	}\s+
			 	subgraph\ clusterorder\ {\s+
			 		label="Ordering\ Contraints";\s+
			 		fontsize=32;\s+
			 		color=black;\s+
			 		(?:[^;}]+;\s+)+
			 	}\s+
				subgraph\ clustermain\ {\s+
			 		label="Profile\ Graph";\s+
			 		fontsize=32;\s+
			 		color=black;\s+
			 		(?:[^;}]+;\s+)+
			 	}\s+
			}
		""", result.stdout, re.VERBOSE)
