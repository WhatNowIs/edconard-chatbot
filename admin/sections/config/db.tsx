import { ExpandableSection } from "@/components/ui/custom/expandableSection";
import { SubmitButton } from "@/components/ui/custom/submitButton";
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

export const DbConfig = ({
  form,
  isSubmitting,
}: {
  form: any;
  isSubmitting: boolean;
}) => {
  return (
    <ExpandableSection
      title={"Database Config"}
      description="Please set the database configuration details. Once set, you will not be able to edit them again."
      open={true}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="db_host"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Database Host</FormLabel>
              <FormControl>
                <Input {...field} placeholder="DB host" />
              </FormControl>
              <FormDescription>
                The URL of where your database is hosted
              </FormDescription>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="db_port"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Database Port</FormLabel>
              <FormControl>
                <Input {...field} placeholder="DB port" />
              </FormControl>
              <FormDescription>
                The port number your database is listening on (default: 5432)
              </FormDescription>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="db_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Database Name</FormLabel>
              <FormControl>
                <Input {...field} placeholder="DB name" />
              </FormControl>
              <FormDescription>
                The name of the specific database you want to connect to
              </FormDescription>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="db_user"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Database Username</FormLabel>
              <FormControl>
                <Input {...field} placeholder="DB username" />
              </FormControl>
              <FormDescription>
                The username for authenticating with the database
              </FormDescription>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="db_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Database Password</FormLabel>
              <FormControl>
                <Input {...field} type="password" placeholder="DB password" />
              </FormControl>
              <FormDescription>
                The password for the specified username
              </FormDescription>
            </FormItem>
          )}
        />
      </div>
      <div className="mt-4 flex justify-end">
        <SubmitButton isSubmitting={isSubmitting} />
      </div>
    </ExpandableSection>
  );
};
