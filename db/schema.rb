# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `rails
# db:schema:load`. When creating a new database, `rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 2020_01_25_003218) do

  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"

  create_table "attendance_submissions", force: :cascade do |t|
    t.bigint "user_id"
    t.datetime "submitted"
    t.bigint "notebook_id"
    t.boolean "was_open"
    t.index ["notebook_id"], name: "index_attendance_submissions_on_notebook_id"
    t.index ["user_id"], name: "index_attendance_submissions_on_user_id"
  end

  create_table "notebooks", force: :cascade do |t|
    t.string "identifier"
    t.boolean "attendance_open"
  end

  create_table "questions", force: :cascade do |t|
    t.bigint "user_id"
    t.bigint "notebook_id"
    t.string "identifier"
    t.string "response"
    t.string "user_hash"
    t.datetime "timestamp"
    t.boolean "locked"
    t.index ["notebook_id"], name: "index_questions_on_notebook_id"
    t.index ["user_id"], name: "index_questions_on_user_id"
  end

  create_table "users", force: :cascade do |t|
    t.string "username"
    t.string "password_hash"
    t.string "api_key"
    t.string "name"
    t.string "email"
  end

end
