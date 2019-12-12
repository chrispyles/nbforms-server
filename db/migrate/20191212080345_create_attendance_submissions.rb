class CreateAttendanceSubmissions < ActiveRecord::Migration[6.0]
  def change
  	create_table :attendance_submissions do |t|
  		t.belongs_to :user
  		t.datetime :submitted
  		t.belongs_to :notebook
  	end
  end
end
