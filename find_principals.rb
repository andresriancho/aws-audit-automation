#
# Find which principals can run a specific API method:
#
#     ruby find_principals.rb lambda:GetFunction
#
# Find which principals can run "A or B"
#
#     ruby find_principals.rb lambda:GetFunction lambda:ListFunctions
#
require 'json'

users = JSON.parse(`aws iam list-users`)['Users'].map { |u| u['Arn'] }
groups = JSON.parse(`aws iam list-groups`)['Groups'].map { |u| u['Arn'] }
roles = JSON.parse(`aws iam list-roles`)['Roles'].map { |u| u['Arn'] }

all = users + groups + roles

actions = ARGV

puts "Searching #{all.size} principals for #{actions} *"
all.each do |arn|
  out = JSON.parse(`aws iam simulate-principal-policy --policy-source-arn #{arn} --action-names #{actions.join(' ')}`)

  allowed = out['EvaluationResults'].select { |res| res["EvalDecision"] == "allowed" }
  unless allowed.empty?
    policies = allowed.map { |r| r['MatchedStatements'].map { |s| s['SourcePolicyId'] } }.flatten.uniq
    puts "* ALLOW: #{arn} by #{policies}"
  end
end
