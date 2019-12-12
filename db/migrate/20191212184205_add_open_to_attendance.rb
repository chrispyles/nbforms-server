class AddOpenToAttendance < ActiveRecord::Migration[6.0]
  def change
  	add_column :attendance_submissions, :was_open, :boolean
  end
end
