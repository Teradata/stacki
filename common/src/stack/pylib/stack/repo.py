import jinja2
import pathlib

yum_repo_template = '/opt/stack/share/templates/yum_repo.j2'

def build_repo_files(box_data, repo_template):
	template_fi = pathlib.Path(repo_template)
	templ = jinja2.Template(template_fi.read_text(), lstrip_blocks=True, trim_blocks=True)
	repo_stanzas = []
	for repo_data in box_data.values():
		for repo in repo_data.values():
			lines = [s for s in templ.render(**repo).splitlines() if s]
			repo_stanzas.append('\n'.join(lines))
	return repo_stanzas
