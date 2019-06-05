import datetime
import logging
import configparser, os
from calendar import monthrange

from dateutil.parser import *
from ..utils.utils import get_scrapper_config

class customTime:
    
    CONFIG = get_scrapper_config()
    LOGGER = logging.getLogger(__name__)

    def __init__(self, news_source, arbitrary_time):
        self.__news_source = news_source
        self.__arbitrary_time = arbitrary_time

        self.__curent_time = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        self.__day_indicator = ''
        self.__hour_indicator = ''
        self.__minute_indicator = ''
        # For dealing with cases like (6 July 2019 - CNBC.com)
        # Where optional split (Tuple): (split_character, date_index)
        self.__optional_split = ''
        self.epoch_time = ''

        # Load data into object
        self.load_format_token()

    def to_epoch_time(self):
        """
        Convert arbitrary time into epoch time
        """
        if self.__optional_split is not None:
            self.__arbitrary_time = self.__arbitrary_time.split(self.__optional_split[0])[self.__optional_split[1]].strip()

        try:
            date_time = self.parse_arbitrary_time_custom()
        except SyntaxError:
            try:
                date_time = parse(self.__arbitrary_time, fuzzy=True)
                # Brute-force
                if "yesterday" in self.__arbitrary_time.lower():
                    date_time.replace(day=date_time.day - 1)
            except Exception as e:
                date_time = None
                self.LOGGER.error("Failed to parse arbitrary time: {}. Exception {}. Assume is None".format(self.__arbitrary_time, e))
        except Exception as e:
            date_time = None
            self.LOGGER.error("Failed to parse arbitrary time: {}. Exception {}. Assume is None".format(self.__arbitrary_time, e))

        self.epoch_time = date_time.timestamp() if date_time is not None else None
        return self.epoch_time

    def parse_arbitrary_time_custom(self):
        """
        Convert arbitrary time into datetime object
        If arbitrary time refers to a time prior to the present eg: 4 hours ago, calculate time based on such information and convert
        
        Returns:
            datetime: datetime object
        
        Raises:
            SyntaxError: Raise error if arbitrary time doesn't contain "ago"
        """
        if not (self.__day_indicator in self.__arbitrary_time or 
                self.__hour_indicator in self.__arbitrary_time or 
                self.__minute_indicator in self.__arbitrary_time):
            raise SyntaxError("Failed to process arbitrary time: {}".format(self.__arbitrary_time))

        publish_time = self.time_ago_parser()
        return publish_time

    def load_format_token(self):
        """
        Load date format token into object
        See headline_scrapper/conf/config.ini
        """
        self.__day_indicator = self.CONFIG['NEWS_DATE_FORMAT'][self.__news_source + '_DAY_FORMAT']
        self.__hour_indicator = self.CONFIG['NEWS_DATE_FORMAT'][self.__news_source + '_HOUR_FORMAT']
        self.__minute_indicator = self.CONFIG['NEWS_DATE_FORMAT'][self.__news_source + '_MINUTE_FORMAT']
        # Check if splitting is required
        try:
            split_at = self.CONFIG['NEWS_DATE_FORMAT'][self.__news_source + '_OPTIONAL_SPLIT']
            date_index = self.CONFIG['NEWS_DATE_FORMAT'][self.__news_source + '_DATE_INDEX']
            self.__optional_split = (split_at, int(date_index))
        except KeyError:
            self.__optional_split = None
        except ValueError as e:
            raise ValueError("Error converting date_index from config.ini, check if data is written correctly")

    def time_ago_parser(self):
        """
        Parse time ago into proper datetime
        Eg: 2 days ago
        """
        parsed_arbitrary_time = self.spacer(self.__arbitrary_time)
        time_element_list = [i for i in parsed_arbitrary_time.split(' ') if i != '']
        publish_time = self.__curent_time

        current_index = 0
        time_ago_dict = {'days': 0, 'hours': 0, 'minutes': 0}
        real_time_dict = {'year': publish_time.year,
                          'month': publish_time.month,
                          'day': publish_time.day,
                          'hour': publish_time.hour,
                          'minute': publish_time.minute}

        while current_index < len(time_element_list):
            # Update day
            if time_element_list[current_index] == self.__day_indicator:
                time_ago_dict['days'] = int(time_element_list[current_index - 1])
            # Update hour
            if time_element_list[current_index] == self.__hour_indicator:
                time_ago_dict['hours'] = int(time_element_list[current_index - 1])
            # Update minute
            if time_element_list[current_index] == self.__minute_indicator:
                time_ago_dict['minutes'] = int(time_element_list[current_index - 1])
            current_index += 1

        real_time_dict['day'] = publish_time.day - time_ago_dict['days']
        real_time_dict['hour'] = publish_time.hour - time_ago_dict['hours']
        real_time_dict['minute'] = publish_time.minute - time_ago_dict['minutes']

        if real_time_dict['minute'] < 0:
            real_time_dict['minute'] += 60
            real_time_dict['hour'] -= 1
        if real_time_dict['hour'] < 0:
            real_time_dict['hour'] += 24
            real_time_dict['day'] -= 1
        if real_time_dict['day'] <= 0:
            real_time_dict['day'] += monthrange(publish_time.year, (publish_time.month - 1))[1]
            real_time_dict['month'] -= 1
        if real_time_dict['month'] <= 0:
            real_time_dict['month'] += 12
            real_time_dict['year'] -= 1

        publish_time = publish_time.replace(year=real_time_dict['year'],
                                            month=real_time_dict['month'],
                                            day=real_time_dict['day'],
                                            hour=real_time_dict['hour'])

        return publish_time

    def spacer(self, string):
        """
        Add space between each word
        Eg: 12hrs -> 12 hrs
        """
        previous_letter_type = int
        parsed_arbitrary_time = ''
        letter_index = 0

        for letter_index, letter in enumerate(string):
            letter = string[letter_index]
            letter_type = None

            try:
                letter = int(letter)
                letter_type = int
            except ValueError:
                letter_type = str

            if letter_type != previous_letter_type:
                parsed_arbitrary_time += ' '
                previous_letter_type = letter_type

            parsed_arbitrary_time += str(letter)

        return parsed_arbitrary_time