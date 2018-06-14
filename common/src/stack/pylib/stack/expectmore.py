import time
import pexpect

from collections import namedtuple

ResponsePair = namedtuple('ResponsePair', ['prompt', 'response'])

# it's best to set expectations early.
class ExpectMoreException(Exception):
	pass

class ExpectMore():
	"""
	Class for wrapping around pexpect
	"""

	def __init__(self, cmd = None, prompts=None):
		self.PROMPTS = ['']
		self.cmd = cmd

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
		if hasattr(self, '_proc') and self._proc.isalive():
			return
		self._proc = pexpect.spawn(self.cmd)


	def end(self, quit_cmd):
		"""
		Terminate the process (if necessary)
		"""
		if not self._proc.exitstatus:
			self._proc.sendline(quit_cmd)
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
			raise ExpectMoreException(f"timed out waiting for expected output '{expected_output}'.\nBuffer: {debug_info}")
		except pexpect.exceptions.EOF:
			raise ExpectMoreException(f"connection to process not available.")

		self.match_index = self._proc.match_index

		output = self._proc.before.decode('utf-8').splitlines()
		# todo: be more clever, throw out garbage first?
		return output



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
		return results


	def ask(self, cmd):
		"""
		Send `cmd` to the process, waiting for a prompt back.  Return the results.
		"""
		results = self.conversation([
			(None, cmd),
			(self.PROMPTS, None)
		])
#		print(results[0])
		return results[0]


	def say(self, cmd):
		self.ask(cmd)

	def __repr__(self):
		return f"{self.__class__.__name__}('{self.cmd}', {self.PROMPTS})"
