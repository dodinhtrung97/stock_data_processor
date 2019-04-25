class Xpath:

	def __init__(self, xpath):
		self.__xpath = xpath if xpath[-1] == r'/' else xpath + r'/'

		self.__xpath_statement_list = []
		self.parsed_statement_list = []

	def to_pattern(self):
		"""
		Parse __xpath into walking_pattern
		Where walking_pattern: list of Tuple(element_name, element_attr_dict, element_index)
		"""
		self.find_all_enclosed_statement()

		parsed_statement_list = []
		for statement in self.__xpath_statement_list:
			parsed_arguments = self.parse_arguments_from_statement(statement)
			parsed_statement_list.append(parsed_arguments)

		self.parsed_statement_list = parsed_statement_list[0] if len(parsed_statement_list) == 1 else parsed_statement_list
		return self.parsed_statement_list

	def find_all_enclosed_statement(self):
		"""
		Fine all statements within xpath
		"""
		xpath_statement_list = []		
		is_statement_start = False

		statement = ""
		for letter in self.__xpath:
			is_statement_start = True if letter == r'/' else False

			if not is_statement_start:
				statement += letter
			else:
				xpath_statement_list.append(statement)
				statement = ""

		processed_statement_list = [statement for statement in xpath_statement_list if statement != '']
		self.__xpath_statement_list = processed_statement_list

	def parse_arguments_from_statement(self, statement):
		"""
		Parse all arguments from statement
		
		Args:
		    statement (TYPE): Description
		
		Returns:
		    TYPE: Description
		
		Raises:
		    ValueError: Description
		"""
		element_name = ""
		element_attr_dict = {}
		element_index = None

		if '[' not in statement:
			element_name = statement
		elif self.is_valid_statement(statement):
			statement_arguments = statement.split('[')
			element_name = statement_arguments[0]

			for argument in statement_arguments[1:]:
				# Slice ']' argument ending from argument
				argument = argument[:-1]
				# Determine if argument is related to attribute searching or index searching
				if '@' in argument:
					element_attr_dict = self.parse_attrs_from_single_argument(argument)
				else:
					try:
						element_index = int(argument)
					except ValueError:
						raise ValueError("Wrong element_index format {}, expect an int".format(argument))

		return (element_name, element_attr_dict) if element_index is None else (element_name, element_attr_dict, element_index)

	def parse_attrs_from_single_argument(self, argument):
		"""
		Parse all attributes from an argument
		
		Args:
		    argument (TYPE): Description
		
		Returns:
		    TYPE: Description
		
		Raises:
		    ValueError: Description
		"""
		attrs = argument.split('and')

		attrs_dict = {}
		for attr in attrs:
			attr = attr.strip()

			if attr[0] != '@':
				raise ValueError("Wrong attribute format {}".format(attr))

			(attr_key, attr_value) = attr.split('=')
			# Remove @ from attr_key
			attr_key = attr_key[1:]
			# Trim string's quota at beginning at last index of attr_value
			attrs_dict[attr_key] = attr_value[1:-1]

		return attrs_dict

	def is_valid_statement(self, statement):
		"""
		Check if a statement is valid
		
		Args:
		    statement (TYPE): Description
		
		Returns:
		    TYPE: Description
		
		Raises:
		    ValueError: Description
		"""
		# 1st statement is element_name
		statement_arguments = statement.split('[')[1:]

		if len(statement_arguments) > 2:
			raise ValueError("Too many arguments within xpath statement {}".format(statement))
		for argument in statement_arguments:
			if argument[-1] != ']':
				raise ValueError("Wrong statement format {}".format(statement))

		return True