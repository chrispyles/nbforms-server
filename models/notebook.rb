class Notebook < ActiveRecord::Base
	has_many :questions
	has_many :attendance_submissions
	validates :identifier, uniqueness: true
end