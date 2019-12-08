class Question < ActiveRecord::Base
	def self.get_or_create_user_submission user_hash, identifier
		Question.where(user_hash: user_hash).where(identifier: identifier).first_or_initialize
	end

	def self.to_2d_array questions, user_hashes
		rows = {}
		if user_hashes
			rows[0] = ['user'] + questions
		else
			rows[0] = questions
		end

		idx = 1
		relation = Question.where(identifier: questions)
		relation.pluck(:user_hash).uniq.each do |user|
			row = []
			if user_hashes
				row << user
			end
			questions.each do |question|
				begin
					response = relation.where(user_hash: user, identifier: question).first.response
				rescue NoMethodError
					response = nil
				end
				row << response
			end
			if row.any?
				rows[idx] = row
				idx += 1
			end
		end
		rows
	end
end