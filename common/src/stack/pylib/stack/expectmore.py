import time
import pexpect

from collections import namedtuple

ResponsePair = namedtuple('ResponsePair', ['prompt', 'response'])

import unicodedata

def remove_control_characters(line):
        line = ''.join(ch for ch in line if unicodedata.category(ch)[0] != 'C')
        if line.startswith(('[?1h', '[K[?')) or line.endswith('[J'):
                line = ''
        return line

# it's best to set expectations early.
class ExpectMoreException(Exception):
	pass

class ExpectMoreTimeoutException(ExpectMoreException):
	pass

class ExpectMore():
	"""
	Class for wrapping around pexpect
	"""

	def __init__(self, cmd = None, prompts=None):
		self.PROMPTS = ['']
		self.cmd = cmd
		self._session_script = []

		if prompts:
			self.PROMPTS = prompts

		if cmd:
			self.start(cmd)


	def start(self, cmd = None):
		"""
		Start `self.cmd` or `cmd` if specified.
		"""
		self.cmd = cmd
		if not self.cmd:
			raise ExpectMoreException('cmd not specified, unable to start')
		if self.isalive():
			return
		self._proc = pexpect.spawn(self.cmd)


	def isalive(self):
		if hasattr(self, '_proc'):
			return self._proc.isalive()
		else:
			return False


	def end(self, quit_cmd):
		"""
		Terminate the process (if necessary)
		"""
		if not self._proc.exitstatus:
			self._proc.sendline(quit_cmd)
			# give some time for the process to send the quit_cmd before terminating,
			# otherwise the quit_cmd might not be run by the process.
			time.sleep(1)
			self._proc.terminate()


	def wait(self, expected_output, timeout=15):
		"""
		Wrap expect to handle disconnections and fetch responses
		`expected_output` can be a string or regex or list of either.
		The index of the first match will be set to self._match_index and the text
		between the last read of the buffer and the match will be returned.
		"""

		try:
			self._proc.expect(expected_output, timeout=timeout)
		except pexpect.exceptions.TIMEOUT:
			for _ in range(10):
				if not self._proc.isalive():
					break
				time.sleep(1)
			debug_info = f'{self._proc.before} {self._proc.buffer} {self._proc.after}'
			raise ExpectMoreTimeoutException(f"timed out waiting for expected output '{expected_output}'.\nBuffer: {debug_info}")
		except pexpect.exceptions.EOF:
			raise ExpectMoreException(f"connection to process not available.")

		self.match_index = self._proc.match_index

		output = self._proc.before.decode('utf-8').splitlines()
		self._session_script.extend(output)

		return output


	def _dump_session(self):
		return self._session_script


	def conversation(self, response_pairs, **kwargs):
		"""
		iterate over response_pairs, calling self._wait() and self._proc.sendline()
		'response_pairs' is a sequence of calls and reposnses which must be of the form ((expected_output, response),)
		kwargs are passed to self._wait()

		"""

		results = []
		for pair in response_pairs:
			r = ResponsePair(*pair)
			if r.prompt:
				results.append(self.wait(r.prompt, **kwargs))
			if r.response:
				self._proc.sendline(r.response)
				self._session_script.append(r.response)
		return results


	def ask(self, cmd, seek=None, sanitizer=None, prompt=None, **kwargs):
		"""
		Send `cmd` to the process, waiting for a prompt back.  Return the results.
		`seek` is a substring to match anywhere in a line of the results.  Results will then be the list of lines starting *after* first substring match.
		`santizer` is a callable which takes a string and outputs a string to transform or remove garbage.  Results will have empty strings removed.
		`prompt` is a string or regex or tuple of these which is the prompt to expect next.  If not set, defaults to self.PROMPTS.
		"""
		if prompt is None:
			prompt = self.PROMPTS

		results = self.conversation(
			[
				(None, cmd),
				(prompt, None)
			],
			**kwargs
		)

		# we only care about the first result
		results = results[0]
		if not sanitizer and not seek:
			return results

		seek_index = 0
		found = False
		new_results = []

		if sanitizer is None:
			sanitizer = lambda s: s

		# at this point we're either sanitizing or seeking or both...
		for line in results:
			line = sanitizer(line)
			if not line:
				# don't keep empty lines
				continue
			new_results.append(line)

			# stop updating the index once we've found
			# if seek is None or is never found, idx will remain 0
			if seek and not found and seek in line:
				found = True
			if seek and not found:
				seek_index += 1

		return new_results[seek_index:]


	def say(self, cmd, **kwargs):
		self.ask(cmd, **kwargs)

	def __repr__(self):
		return f"{self.__class__.__name__}('{self.cmd}', {self.PROMPTS})"
