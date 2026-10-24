"""Drive the real guided onboarding when preparing an unrelated test fixture."""
def tutorial_action(activity,uid,body):
 action=body.get('action');step=body.get('step')
 if action in ('tutorial_next','tutorial_finish') and type(step) is int and 0<=step<len(activity.tutorial.destinations):
  state=activity.tutorial.state(uid)
  if state['step']==step and (not state['completed'] or state['replay']):
   activity.action(uid,dict(action='tutorial_visit',step=step,destination=activity.tutorial.destinations[step]))
 return activity.action(uid,body)
