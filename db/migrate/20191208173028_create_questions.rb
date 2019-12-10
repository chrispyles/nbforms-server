class CreateQuestions < ActiveRecord::Migration[6.0]
  def change
  	create_table :questions do |t|
  		t.belongs_to :user
	  	t.string :identifier
	  	t.string :response
	  	t.string :user_hash
	  	t.string :notebook
	  	t.datetime :timestamp
	  end
	end
end
